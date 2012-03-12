from tg import app_globals as gl

root_key = 'Operations'


def get_operations_paths():
    plugs = gl.plugin_manager.getAllPlugins()
    return mix_plugin_paths(plugs)


def mix_plugin_paths(plugins):
    '''
    Mix all plugin paths to make one in order to draw hierarchy buttons on the interface.
    '''
    
    paths = []
    for plug in plugins:
        paths.append(plug.plugin_object.path())
    return pathify(paths)
            
            
          

class Node(object):
    
    def __init__(self, key):
        self.childs = []
        self.key = key
    
    def add(self, child):
        self.childs.append(child)
    
    def has_child(self, child):
        return self.childs.count(child) > 0
    
    def get_child(self, child):
        return self.childs[self.childs.index(child)]
    
    def __eq__(self, o):
        return self.key == o.key
    
    # def __repr__(self, *args, **kwargs):
    #     return '<%s childs : %s >' % (self.key ,self.childs)
    
def encode_tree(obj):
    '''
    JSON function to make recursive nodes being JSON serializable
    '''
    if not isinstance(obj, Node):
        raise TypeError("%r is not JSON serializable" % (o,))
    return obj.__dict__


def mix(node, path, index):
    '''
    Mix path with the node
    '''
    if(index < len(path)):
        p = Node(path[index])
        if node.has_child(p):
            new = node.get_child(p)
        else :
            new = p
            node.add(p)
        mix(new, path, index + 1)
    

def pathify(paths):
    '''
    Mix a list of paths together
    '''
    root = Node(root_key)
    for path in paths:
        mix(root, path, 0)
    return root



