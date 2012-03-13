from tg import app_globals as gl

root_key = 'Operations'




def get_plugin_byId(_id):
    if(_id):
        plugs = gl.plugin_manager.getAllPlugins()
        for p in plugs :
            if p.plugin_object.unique_id() == str(_id) : return p

def get_operations_paths():
    plugs = gl.plugin_manager.getAllPlugins()
    return mix_plugin_paths(plugs)


def mix_plugin_paths(plugins):
    '''
    Mix all plugin paths to make one in order to draw hierarchy buttons on the interface.
    '''
    
    nodes = []
    for plug in plugins:
        o = plug.plugin_object
        nodes.append(o)
    return pathify(nodes)
            
            
          

class Node(object):
    
    def __init__(self, key):
        self.childs = []
        self.key = key
        self.id = None
        
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
        raise TypeError("%r is not JSON serializable" % (obj,))
    return obj.__dict__


def mix(node, path, index, uid=None):
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
        mix(new, path, index + 1, uid)
    else :
        node.id = uid

def pathify(nodes):
    '''
    Mix a list of paths together
    '''
    root = Node(root_key)
    for n in nodes:
        mix(root, n.path(), 0, n.unique_id())
    return root



