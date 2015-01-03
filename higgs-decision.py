import os
import math

def attribute_value(instance, attribute, attribute_names):
    '''Returns the value of attribute in instance, based on the position of attribute in the list of attribute_names'''
    if attribute not in attribute_names:
        return None
    else:
        i = attribute_names.index(attribute)
        return instance[i] # using the parameter name here

def print_attribute_names_and_values(instance, attribute_names):
  for i in range(len(attribute_names)):
    print (attribute_names[i], '=', attribute_value(instance, attribute_names[i], attribute_names))




def load_higgs_instances(filename):
  
	instanceList = []

	with open(filename, 'r') as f:
		currentLine = 0 # counter for which line we are currently iterating over
#		maxNumberOfEntries = 1000000
		for line in f:
			entry = line.strip().split(',')

			entry[0] = int(float(entry[0]))
			instanceList.append(entry)

#			currentLine += 1
#			if currentLine == 1000:
#				break

	return instanceList


def entropy(instances):
    pcnt = ecnt = 0.0
    for i in instances:
        if i[0] == 0:
            pcnt = pcnt + 1
        else:
            ecnt = ecnt + 1
    tot = pcnt + ecnt
    p1 = pcnt / tot	   
    p2 = ecnt / tot
    if (p1 == 0 and p2 == 1) or (p1 == 1 and p2 == 0):
        return 0
    entropy = - p1 * math.log(p1,2) - p2 * math.log(p2,2)
    return (entropy)



def print_all_attribute_value_counts(instances, attribute_names):
    for j in range(len(attribute_names)):
        print (attribute_names[j])
        v_counts = defaultdict(int)

        for inst in instances:
            val = inst[j]
            v_counts[val] += 1
        for value in v_counts:
            print (value,':', v_counts[value])




import operator
from collections import defaultdict # don't need to use collections.defaultdict() below

from collections import Counter

def information_gain(instances, i):
    '''IG achieved for set instances with attribute i'''
    entropy_s = entropy(instances)
    set_size = len(instances)
    res = defaultdict(float)
    maxval = 0

    subset_val = 0
    v_counts = defaultdict(int)
    v_instances = defaultdict(list)
    
    for inst in instances:
    
        val = inst[i]
        v_counts[val] += 1
        v_instances[val].append(inst)
    for value in v_counts:
        p_si = v_counts[value] / set_size
        entropy_si = entropy(v_instances[value])
        currval = (p_si * entropy_si)
        subset_val = subset_val + currval
    IG = entropy_s - subset_val
    return IG
            


def split_instances(instances, attribute_index):
    '''Returns a list of dictionaries, splitting a list of instances according to their values of a specified attribute''
    
    The key of each dictionary is a distinct value of attribute_index,
    and the value of each dictionary is a list representing the subset of instances that have that value for the attribute'''
    partitions = defaultdict(list)
    for instance in instances:
        partitions[instance[attribute_index]].append(instance)
        
    return partitions


def choose_best_attribute_index(instances, candidate_attribute_indexes, class_index=0):
    maxval = 0
    best_index = 0
    for i in candidate_attribute_indexes:
        IG = information_gain(instances, i)
        if IG > maxval:
            maxval = IG
            best_index = i

    return best_index



def majority_value(instances, class_index=0):
  partitions = split_instances(instances, class_index)
  max = 0
  for val in (0,1):   # should look up these values based on class_index using attribute_names_and_values
    n = len(partitions[val])
    if n >= max:
      max = n
      maj_val = val

  return maj_val

def create_decision_tree(instances, candidate_attribute_indexes=None, class_index=0, default_class=None, trace=0):
    '''Returns a new decision tree trained on a list of instances.
        
        The tree is constructed by recursively selecting and splitting instances based on
        the highest information_gain of the candidate_attribute_indexes.
        
        The class label is found in position class_index.
        
        The default_class is the majority value for the current node's parent in the tree.
        A positive (int) trace value will generate trace information with increasing levels of indentation.
        
        Derived from the simplified ID3 algorithm presented in Building Decision Trees in Python by Christopher Roach,
        http://www.onlamp.com/pub/a/python/2006/02/09/ai_decision_trees.html?page=3'''
    
    # if no candidate_attribute_indexes are provided, assume that we will use all but the target_attribute_index
    if candidate_attribute_indexes is None:
        candidate_attribute_indexes = range(len(instances[0]))
        candidate_attribute_indexes.remove(class_index)
    
    class_labels_and_counts = Counter([instance[class_index] for instance in instances])

    # If the dataset is empty or the candidate attributes list is empty, return the default value
    if not instances or not candidate_attribute_indexes:
        if trace:
            print '{}Using default class {}'.format('< ' * trace, default_class)
            return default_class
    
    # If all the instances have the same class label, return that class label
    elif len(class_labels_and_counts) == 1:
        class_label = class_labels_and_counts.most_common(1)[0][0]
        if trace:
            print '{}All {} instances have label {}'.format('< ' * trace, len(instances), class_label)
        return class_label
    else:
        default_class = majority_value(instances, class_index)
        
        # Choose the next best attribute index to best classify the instances
        best_index = choose_best_attribute_index(instances, candidate_attribute_indexes, class_index)
        if trace:
            print '{}Creating tree node for attribute index {}'.format('> ' * trace, best_index)

        # Create a new decision tree node with the best attribute index and an empty dictionary object (for now)
        tree = {best_index:{}}

    # Create a new decision tree sub-node (branch) for each of the values in the best attribute field
    partitions = split_instances(instances, best_index)
    
    # Remove that attribute from the set of candidates for further splits
    remaining_candidate_attribute_indexes = [i for i in candidate_attribute_indexes if i != best_index]
    for attribute_value in partitions:
        if trace:
            print '{}Creating subtree for value {} ({}, {}, {}, {})'.format(
                                                                                '> ' * trace,
                                                                                attribute_value,
                                                                                len(partitions[attribute_value]),
                                                                                len(remaining_candidate_attribute_indexes),
                                                                                class_index,
                                                                                default_class)
            
            # Create a subtree for each value of the the best attribute
            subtree = create_decision_tree(
                                           partitions[attribute_value],
                                           remaining_candidate_attribute_indexes,
                                           class_index,
                                           default_class,
                                           trace + 1 if trace else 0)
                                           
                                           # Add the new subtree to the empty dictionary object in the new tree/node we just created
        tree[best_index][attribute_value] = subtree

    return tree

clean_instances = load_higgs_instances('../HIGGS.csv')

# split instances into separate training and testing sets
training_instances = clean_instances[:-500]
tree = create_decision_tree(training_instances, trace=1) # remove trace=1 to turn off tracing
            
