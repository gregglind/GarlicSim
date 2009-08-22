

import misc.queuetools as queuetools
from crunchers import CruncherThread, CruncherProcess
from misc.infinity import Infinity

PreferredCruncher = [CruncherThread, CruncherProcess][1]
# Should be a nicer way of setting that.


class CrunchingManager(object):
    def __init__(self, project):
        
        self.project = project
        
        if project.simpack_grokker.history_dependent:
            self.Cruncher = CruncherThread
        else:
            self.Cruncher = PreferredCruncher
        
        
        self.crunchers = {}
        """
        A dict that maps leaves that should be worked on to crunchers.
        """
    
    def sync_crunchers(self, temp_infinity_node=None):
        """
        Talks with all the crunchers, takes work from them for
        implementing into the Tree, terminates crunchers or creates
        new crunchers if necessary.
        You can pass a node as `temp_infinity_node`. That will cause this
        function to temporarily treat this node as if it should be crunched
        indefinitely.

        Returns the total amount of nodes that were added to the tree.
        """

        with self.project.tree_lock.write:
            tree = self.project.tree
            my_leaves_to_crunch = self.project.leaves_to_crunch.copy()
    
            if temp_infinity_node:
                if self.project.leaves_to_crunch.has_key(temp_infinity_node):
                    had_temp_infinity_node = True
                    previous_value_of_temp_infinity_node = \
                            self.project.leaves_to_crunch[temp_infinity_node]
                else:
                    had_temp_infinity_node = False
                my_leaves_to_crunch[temp_infinity_node] = Infinity
    
    
            added_nodes = 0
    
            for leaf in self.crunchers.copy():
                if not (leaf in my_leaves_to_crunch):
                    cruncher = self.crunchers[leaf]
                    result = queuetools.dump_queue(cruncher.work_queue)
    
                    cruncher.retire()
    
                    current = leaf
                    for state in result:
                        current = tree.add_state(state, parent=current)
                    added_nodes += len(result)
    
                    del self.crunchers[leaf]
                    #cruncher.join() # todo: sure?
    
    
    
            for (leaf, number) in my_leaves_to_crunch.items():
                if self.crunchers.has_key(leaf) and self.crunchers[leaf].is_alive():
    
                    cruncher = self.crunchers[leaf]
                    result = queuetools.dump_queue(cruncher.work_queue)
    
                    current = leaf
                    for state in result:
                        current = tree.add_state(state, parent=current)
                    added_nodes += len(result)
    
                    del my_leaves_to_crunch[leaf]
    
    
                    if number != Infinity: # Maybe this is just a redundant dichotomy from before I had Infinity?
                        new_number = number - len(result)
                        if new_number <= 0:
                            cruncher.retire()
                            #cruncher.join() # todo: sure?
                            del self.crunchers[leaf]
                        else:
                            my_leaves_to_crunch[current] = new_number
                            del self.crunchers[leaf]
                            self.crunchers[current] = cruncher
    
                    else:
                        my_leaves_to_crunch[current] = Infinity
                        del self.crunchers[leaf]
                        self.crunchers[current] = cruncher
    
                    if leaf == temp_infinity_node:
                        continuation_of_temp_infinity_node = current
                        progress_with_temp_infinity_node = len(result)
    
    
    
    
                else:
                    # Create cruncher
                    if leaf.still_in_editing is False:
                        cruncher = self.crunchers[leaf] = self.create_cruncher(leaf)
                    if leaf == temp_infinity_node:
                        continuation_of_temp_infinity_node = leaf
                        progress_with_temp_infinity_node = 0
    
            if temp_infinity_node:
                if had_temp_infinity_node:
                    temp = max(previous_value_of_temp_infinity_node - \
                               progress_with_temp_infinity_node, 0)
                    
                    my_leaves_to_crunch[continuation_of_temp_infinity_node] = temp
                                       
                else:
                    del my_leaves_to_crunch[continuation_of_temp_infinity_node]
    
            self.project.leaves_to_crunch = my_leaves_to_crunch
    
            return added_nodes
        
    def create_cruncher(self, node):
        """
        Creates a cruncher and tells it to start working on `node`.
        """
        step_function = self.project.simpack_grokker.step
        
        if self.Cruncher == CruncherProcess:
            cruncher = self.Cruncher(node.state,
                                     step_function=step_function)
        
        else: # self.Cruncher == CruncherThread
            cruncher = self.Cruncher(node.state, self.project,
                                    step_function=step_function)
        cruncher.start()
        return cruncher