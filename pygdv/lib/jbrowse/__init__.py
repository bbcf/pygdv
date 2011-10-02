'''
Contains everything that touch to JBrowse
'''
import math, sqlite3





'''
Number of scores per images = tab width
'''
TAB_WIDTH = 100



'''
Zooms available in JBrowse.
'''
zooms = (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000,
        2000, 5000, 10000, 20000, 50000, 100000)






def get_image_nb(position, zoom):
    '''
    Get the image number to put in the sqlite database.
    @param position : the position of the cursor
    @param zoom : the zoom
    '''
    return math.ceil(position/TAB_WIDTH)/zoom


def get_tab_index(position, zoom):
    '''
    Get the index of the tab for the position specified.
    @param position : the position of the cursor
    @param zoom : the zoom
    '''
    return math.ceil(position/zoom)%TAB_WIDTH



def do(database, chromosome, output):
    '''
    Get the features in the database for the chromosome specified.
    '''
    zoom = 1
    
    manager = SQLiteManager.connect(database, chromosome, output)
    
    cursor = manager.get_features()
    
    prev_img_nb_stop = prev_tab_index_stop = prev_stop = None
    
    prev_stop = None
    
    for row in cursor :
        start = row[0]
        stop = row[1]
        score = row[2]
        
        print 'start : %s, stop: %s (score : %s)' % (start, stop, score)
        
        # get where to start
        img_nb_start = get_image_nb(start, zoom)
        tab_index_start = get_tab_index(start, zoom)
        
        # write previous stop (if)
        ''' if the previous end of the feature is just next to the next one, doesn't write the previous end to 0.0 score'''
        if prev_stop is not None and not prev_stop+1 == start:
            fstop = prev_stop + 1
            img_nb = get_image_nb(fstop, zoom)
            tab_ind = get_tab_index(fstop, zoom)
            manager.add_tuple(img_nb, tab_ind, 0)

        # write current
        manager.add_tuple(img_nb_start, tab_index_start, score)

        # remember value for next iteration        
        prev_stop = stop
    
    # write final stop
    fstop = prev_stop + 1
    img_nb = get_image_nb(fstop, zoom)
    tab_ind = get_tab_index(fstop, zoom)
    manager.add_tuple(img_nb, tab_ind, 0)
    
    
    # close cursor
    cursor.close()
    
    
    manager.close()
    
    
    
    
    
    
class SQLiteManager(object):
    '''
    Link between the algorith and the SQLite database
    '''
    
    SIZE_LIMIT = 1024
    
    @classmethod
    def connect(cls, database, chromosome, output):
        '''
        @param database : the database to connect to
        @param output : where to write the values after computation. This is a DIRECTORY.
        @param chromosome : the chromosome to get the features from
        '''
        obj = cls(chromosome,output)
        obj.conn = sqlite3.connect(database)
        return obj
        
    @classmethod    
    def new(cls, connection, chromosome, output):
        '''
        @param connection : the connection to the database
        @param output : where to write the values after computation. This is a DIRECTORY.
        @param chromosome : the chromosome to get the features from
        '''
        obj = cls(chromosome, output)
        obj.conn = connection
        return obj
        
            
    def __init__(self, chromosome, output):
        self.chromosome = chromosome
        
        
        # init output
        self.output = output
        self.output_conn = sqlite3.connect('%s/%s.sqlite3' % (self.output, self.chromosome))
        self.output_cursor = self.output_conn.cursor()
        self.output_cursor.execute('CREATE TABLE sc (number INT, pos INT, score REAL)')
        '''
        @param tuples : containing tuples to write
        '''
        self.tuples = []
        '''
        @param cur_size : the current size of self.tuples
        '''
        self.cur_size = 0
        '''
        @param no_values : True if all values in self.tuples are written
        '''
        self.no_values = True
        
        
        
    def add_tuple(self, x, y, z):    
        '''
        Put value to write in the db in memory to build a generator in order to 
        speed up SQL efficiency
        '''
        self.no_values = False
        self.cur_size+=1
        self.tuples.append((x, y, z))
        
        if self.cur_size >= self.SIZE_LIMIT:
            self.cur_size = 0
            self.no_values = True
            self.write_tuples()
            self.tuples = []
        
        
    def close(self):
        if not self.no_values:
            self.write_tuples()
        self.conn.commit()
        self.conn.close()
        self.output_conn.commit()
        self.output_cursor.close()
        self.output_conn.close()
        
    def get_features(self):
        '''
        Get the features on a chromosome.
        @param chromosome : the chromosome
        @return a Cursor Object
        '''
        cursor = self.conn.cursor()
        return cursor.execute('select start, end, score from "%s"' % self.chromosome)
    
    def write_tuples(self):
        '''
        Write tuples in the oupput specified.
        '''
        self.output_cursor.executemany('insert into sc values (?, ?, ?);', self.tuples)
        self.output_conn.commit()









import sys

if __name__ == '__main__':
    database = sys.argv[1]
    output = sys.argv[2]
    chromosome = sys.argv[3]
    do(database, chromosome, output)












    