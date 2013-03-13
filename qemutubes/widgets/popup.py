from tw2.jqplugins.ui import DialogWidget
from tw2.core import JSSource

class PopUp(DialogWidget):
    id = 'qtpopup'
    options = {'title': 'Q-Tubes', 'autoOpen': False,
               'modal': True, }
    value="""
   <iframe id="qtpopup_frame" frameborder="no">
      <p>Loading...</p>
   </iframe>
   """
    linkclass = 'qtpopup'

    def prepare(self):
        popup_js = JSSource(location='head',
                            src = """
  $(document).ready(function() {
  $("#%(popup)s")[0].loadPage = function(e) { 
         e.preventDefault(); 
         popup=$("#%(popup)s");
         frame=$("#%(popup)s_frame")
         //frame.contents().find('html').html('<p>Loading...</p>');
         popup.dialog('option', 'title', 'Loading...');
         popup.dialog('open');
         frame.attr('src', $(this).attr('href'));
  };
  $('#%(popup)s > iframe').load(function () {
         $(this).height($(this).contents().height());
         $(this).width($(this).contents().width());
         $('#%(popup)s').dialog('option', 'width', $(this).contents().width()+40);
         $('#%(popup)s').dialog('option', 'title', '%(title)s');
  });         
  $("a.%(lclass)s").click($("#%(popup)s")[0].loadPage );
  });
""" % {'popup': self.id, 'lclass': self.linkclass, 'title': self.options['title'] })
        self.resources.append(popup_js)
        super(PopUp, self).prepare()
    
    
