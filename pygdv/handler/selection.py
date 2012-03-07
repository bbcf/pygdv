from pygdv.model import DBSession, Selection, Location
import json

def selections(project_id):
    selections = DBSession.query(Selection).filter(Selection.project_id == project_id).all()
    sel_list = []
    for sel in selections:
        sel_obj = {'id' : sel.id, 'description' : sel.description, 'color' : sel.color}
        loc_list = []
        for loc in sel.locations:
            loc_list.append({'chr' : loc.chromosome,
                      'start' : loc.start,
                      'end' : loc.end,
                      'id' : loc.id,
                      'desc' : loc.description})
        sel_obj['locations'] = loc_list
        sel_list.append(sel_obj)
    return json.dumps(sel_list)