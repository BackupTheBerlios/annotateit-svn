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

<script language="JavaScript1.1" type="text/javascript">
<!--
function login() {
  var emailAddress = document.forms[0].emailAddress.value;
  var password = document.forms[0].password.value;
  var randomValue = '[% randomValue %]';
  var conglomeration  = password + randomValue;
  var authHash = calcMD5(conglomeration);
  document.forms[0].authHash.value = authHash;
  document.forms[0].password.value = "";
  document.forms[0].randomValue.value = randomValue;
  document.forms[0].submit();
   

}
//-->
</script>
