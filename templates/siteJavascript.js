[%# Copyright 2003, Buzzmaven Co.

# This file is part of Annotateit.

# Annotateit is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# Annotateit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Annotateit (see GNU-GPL.txt); if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.
# The GNU General Public License may also be found on the Web at:
#   http://www.gnu.org/licenses/gpl.txt 

%]
<script language="JavaScript1.2" type="text/javascript">
<!--
var textAry = new Array();
[% FOREACH textAry %]textAry[[% index %]] = '[% Value %]';
[% END %]

var titleAry = new Array();
[% FOREACH textAry %]titleAry[[% index %]] = '[% Label %]';
[% END %]
function getOpenerSel() {
  var txt = new String;
  if (opener.getSelection) txt = opener.getSelection();
  else if (opener.document.getSelection) txt = opener.document.getSelection();
  else if (opener.document.selection.createRange) txt = opener.document.selection.createRange().text; 
  else return
  txt = cleanSelection(txt);
  document.forms[0].selectedtext.value = txt == '' ? '(Whole Page)' : txt;

}

function switchText() {
  var i = document.forms[0].predefined.selectedIndex;
  document.forms[0].title.value = titleAry[i];
  document.forms[0].annotation.value = textAry[i];

}

function cleanSelection(sel) {
  var r = sel.toString();
  var pattern = new RegExp("\\{\\{[^\\]]*\\}\\}","g");
  r = r.replace(pattern,"");
  var pattern = new RegExp("-\\[[^\\]]+\\]-","g");
  r = r.replace(pattern,"");
  var pattern = new RegExp("\\s+","g");
  r = r.replace(pattern," ");

  return r;
}
  


//-->
</script>
