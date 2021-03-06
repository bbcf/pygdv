from pygdv.lib import constants
from tg import url
import genshi

tooltip = {}

def help_address(hurl, section, title):
    return genshi.Markup(
         '''
        <a href="%s#%s" title="%s">
        <img src="../images/question.png" width="16" height="16"/></a>
        </a>
         ''' % (hurl, section, title)
    )

def make_tooltip(title, message):
    return genshi.Markup(
        '''
            <div class='tooltip_gdv'>
                <div class='tooltip_hider'></div>
                <span class='tooltip_pane'>
                <div class='tooltip_title'><h3>%s</h3></div>
                <div class='tooltip_body'>%s</div>
                </span>
            </div>
        ''' % (title, message))






tooltip['circle'] = make_tooltip('Circle', '''A circle is a group of person you may want to collaborate with.
You can create a new one by clicking 'Add circle' link. You can also tweak the permissions to give to each circle.
<ul>
    <li><a class='action delete_link'></a>  delete the circle.</li>
    <li><a class='action edit_link'></a>  edit the circle : change its name, its description, add/remove users.</li>
</ul>
''')

tooltip['circledesc'] = make_tooltip('Add user', '''Here you see the list of persons who are in ths circle.
<ul>
    <li><a class='action delete_link'></a>  remove the person from the circle.</li>
    <li><a class='action add_link'></a>  add a person to this circle.</li>
</ul>
''')

tooltip['job'] = make_tooltip('Job', '''A Job is a result from a request you send from the view. To make a new one, go to Projects page and click on <a class='action view_link'></a>.
<ul>
    <li><a class='action delete_link'></a>  delete the job.</li>
    <li>result : get the job's result.</li>
</ul>

''' )

tooltip['track'] = make_tooltip('Track', '''A track is equivalent to a genomic file. You can upload a new one by clicking 'new track' link.
Input supported are %s.
<ul>
    <li><a class='action export_link'></a>  download the track in a specified format.</li>
    <li><a class='action delete_link'></a>  delete the track.</li>
    <li><a class='action edit_link'></a>  edit the track (change its name, its color)</li>
</ul>


''' % (', '.join(constants.formats_supported)))

tooltip['project'] = make_tooltip('Project', '''A project is a playlist of track : You can visualize them, play with them ...
<ul>
    <li><a class='action edit_link'></a>  add track to the project, change its name.</li>
    <li><a class='action view_link'></a>  visualize the project.</li>
    <li><a class='action share_link'></a>  share the project with others.</li>
    <li><a class='action delete_link'></a>  delete the project (not the track associated).</li>
    <li><a class='action detail_link'></a>  Detailed project.</li>
</ul>
''')

tooltip['links'] = make_tooltip('Links to your project', '''You can give these links to other people (right-click > copy link). They will be able to directly see the project by clicking this link.
<ul>
    <li>public link : user will only be able to visualize the project..</li>
    <li>import link : user will be able to import the project in his profile. It means that he can access every data in the project.</li>
</ul>
''')

tooltip['permissions'] = make_tooltip('Customize permissions', '''There are several permissions that you can give to circles :
<ul>
    <li>read : users will only be able to visualize the project.</li>
    <li>download : users will be able to access the data in the project.</li>
    <li>upload : users will be able to contribute on the project, like uploading new data on it.</li>
</ul>
''')

tooltip['read'] = make_tooltip('Read permission', '''A circle with this permission can only visualize the data on the project.''')

tooltip['download'] = make_tooltip('Download permission', '''A circle with this permission can download the data associated with the project.''')

tooltip['upload'] = make_tooltip('Upload permission', '''A circle with this permission can upload data on the project.''')

tooltip['task'] = make_tooltip('Task', '''A task is a job launched on Celery.''')

tooltip['admin'] = make_tooltip('Admin', '''You found the admin secret place :D Congratulations !!! ''')