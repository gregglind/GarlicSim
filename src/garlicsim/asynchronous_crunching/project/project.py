# Copyright 2009 Ram Rachum.
# This program is distributed under the LGPL2.1 license.

"""
This module defines the Project class. See its documentation for more
information.
"""

import garlicsim.data_structures
import garlicsim.simpack_grokker
import crunching_manager

import garlicsim.misc.read_write_lock as read_write_lock
from garlicsim.misc.infinity import Infinity
import garlicsim.misc.module_wrapper
import garlicsim.misc.cool_dict

__all__ = ["Project"]

class Project(object):
    """
    You create a project when you want to do a simulation which will crunch
    in the background with worker threads or worker processes.

    A project contains within it a tree.
        
    The crunching is taken care of by the CrunchingManager which is a part of
    every project. The CrunchingManager employs CruncherThreads and/or
    CruncherProcesses to get the work done. To make the CrunchingManager take
    work from the crunchers and coordinate them, call the sync_crunchers method
    of the project.
    
    What the crunching manager's sync_crunchers method will do is check the
    attribute .nodes_to_crunch of the project. This attribute is a dict-like
    object which maps nodes that should be crunched to a number specifying how
    many states should be crunched from this node. The crunching manager will
    then coordinate the crunchers in order to do this work. It will update the
    .nodes_to_crunch attribute when the crunchers have completed some of the
    work.
    """

    def __init__(self, simpack):
        
        wrapped_simpack = \
            garlicsim.misc.module_wrapper.module_wrapper_factory(simpack)
        
        self.simpack_grokker = \
            garlicsim.simpack_grokker.SimpackGrokker(wrapped_simpack)
        
        self.simpack = wrapped_simpack

        self.tree = garlicsim.data_structures.Tree()
        
        self.crunching_manager = crunching_manager.CrunchingManager(self)
        
        self.tree_lock = read_write_lock.ReadWriteLock()
        """
        The tree_lock is a read-write lock that guards access to the tree.
        We need such a thing because some simulations are history-dependent
        and require reading from the tree in the same time that sync_crunchers
        could potentially be writing to it.
        """

        self.nodes_to_crunch = garlicsim.misc.cool_dict.CoolDict()
        """
        A dict that maps leaves that should be worked on to a number specifying
        how many nodes should be created after them.
        """

    def make_plain_root(self, *args, **kwargs):
        """
        Creates a parentless node, whose state is a simple plain state.
        The simulation package should define the function `make_plain_state`
        for this to work.
        Returns the node.
        """
        state = self.simpack.make_plain_state(*args, **kwargs)
        return self.root_this_state(state)

    def make_random_root(self, *args, **kwargs):
        """
        Creates a parentless node, whose state is a random and messy state.
        The simulation package should define the function `make_random_state`
        for this to work.
        Returns the node.
        """
        state = self.simpack.make_random_state(*args, **kwargs)
        return self.root_this_state(state)

    def root_this_state(self, state):
        """
        Takes a state, wraps it in a node and adds to the tree without a
        parent.
        Returns the node.
        """
        return self.tree.add_state(state)

    def crunch_all_leaves(self, node, wanted_distance):
        """
        Orders to start crunching from all the leaves of `node`, so that there
        will be a buffer whose length is at least `wanted_distance`.
        """
        leaves = node.get_all_leaves(wanted_distance)
        for (leaf, distance) in leaves.items():
            new_distance = wanted_distance - distance
            self.nodes_to_crunch.raise_to(leaf, new_distance)

    def sync_crunchers(self, temp_infinity_node=None):
        """
        Talks with all the crunchers, takes work from them for
        implementing into the tree, terminates crunchers or creates
        new crunchers if necessary.
        You can pass a node as `temp_infinity_node`. That will cause this
        function to temporarily treat this node as if it should be crunched
        indefinitely.

        Returns the total amount of nodes that were added to the tree.
        """
        
        return self.crunching_manager.sync_crunchers \
               (temp_infinity_node=temp_infinity_node)
    
    def __getstate__(self):
        my_dict = dict(self.__dict__)
        
        del my_dict["tree_lock"]
        del my_dict["crunching_manager"]
        
        return my_dict
    
    def __setstate__(self, pickled_project):
        self.__init__(pickled_project["simpack"])
        self.__dict__.update(pickled_project)