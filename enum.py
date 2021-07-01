# sysadm/enum.py
version = '2017.04.14'

# This is enum.py, a small utility which helps one deal with enumeration
# (of formulas, of theorems, of chapters, etc) when writing documents.

# Copyright Cristian Barbarosie 2005-2017

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, see http://www.gnu.org/licenses/

# This program, as well as a user's manual, can be downloaded from
# http://cristian-barbarosie.blogspot.com/p/english.html

# exit codes : 0 on success
#              1 for command line parsing error
#              2 if trying to remove an existing numbering

import sys, getopt, tempfile, os, re, shutil

def usage (stat=1) :
  if sys.platform in ['win32']:
    print 'usage:'
    print ' python enum.py insert "(\\formula 3.4)" paper.tex cap1.tex'
    print ' python enum.py remove "(\\formula 3.4)" paper.tex cap1.tex'
    print ' python enum.py switch "(\\formula 3.4)" 7 paper.tex cap1.tex'
#    print ' python enum.py switch-cond "\\cap " 4 5 ".\\formula " ">" 21 paper.tex cap1.tex'
    print ' python enum.py version'
    print ' python enum.py help'
  else :
    print "usage:"
    print " python enum.py insert '(\\formula 3.4)' paper.tex cap1.tex"
    print " python enum.py remove '(\\formula 3.4)' paper.tex cap1.tex"
    print " python enum.py switch '(\\formula 3.4)' 7 paper.tex cap1.tex"
#    print " python enum.py switch-cond '\\cap ' 4 5 '.\\formula ' '>' 21 paper.tex cap1.tex"
    print ' python enum.py version'
    print ' python enum.py help'
  if stat > 0 : sys.exit(stat)

# We use global variables, gathered together under the name 'gv'.
  
class MyClass : pass
gv = MyClass()

class MyError(Exception) : pass

args = sys.argv
gv.optlist,gv.args = getopt.getopt (args,'v')

if len(gv.args) < 3 : usage ()

def my_rename (temp_name,file_name,did_change) :
  if did_change :
    os.remove (file_name)
    try :
      os.rename (temp_name,file_name)
    except OSError :
      try :
        shutil.copy (temp_name,file_name)
      except OSError :
        print "there was an error while trying to copy"
        print temp_name,"onto",file_name,'.'
        print file_name,"has been deleted !"
        print "Please take appropriate action."
      else :
        os.remove (temp_name)
  else : # didn't change
    os.remove (temp_name)

# The "lengine" routine was introduced in April 2017.
# I wanted to allow patterns to extend to two consecutive lines
# ( no more than two ! ).
# The "engine" does everything except the very modification
# of the numbers, which is delegated to the other functions
# (insert, remove, etc).

# We begin with an empty "head", search for the base_pattern
# in the "tail". When we find the pattern, we modify
# that portion accordingly and add it to the "head",
# removing it from the "tail".

def engine (modifier, file_name) :
  # 'modifier' is a routine like 'insert', 'remove' or 'switch'
  f = file (file_name,'r')
  temp_name = tempfile.mktemp()
  temp_file = file (temp_name,'w')
  did_change = False
  tail = ''
  head = ''
  for line in  f :
    tail += line
    while True :
      m = gv.base_pat.search (tail)
      if not m : break
      n = int(m.group(1))
      new_n = modifier (n)
      if new_n != n :
        did_change = True
        head += tail[:m.start(1)] + str(new_n) + tail[m.end(1):m.end()]
        tail = tail[m.end():]
      else :
        head += tail[:m.end()]
        tail = tail[m.end():]
    ll = []
    p = 0
    while True :
      m = gv.newline_pat.search(tail,p)
      if not m : break
      p = m.end()
      ll.append (p)
    if len(ll) > 1 :
      pos = ll[-2]
      head = head + tail[:pos]
      tail = tail[pos:]
    temp_file.write (head)
    head = ''
  temp_file.write (tail)
  del f,temp_file
  my_rename (temp_name,file_name,did_change)

# This version of engine only checks, does not modify anything
def engine_ro (modifier, file_name) :
  # 'modifier' should be 'check_before_remove'
  f = file (file_name,'r')
  tail = ''
  head = ''
  line_number = 0
  for line in  f :
    line_number += 1
    tail += line
    while True :
      m = gv.base_pat.search (tail)
      if not m : break
      n = int(m.group(1))
      cond = modifier (n)
      if cond :
        print gv.error_message % {'line':line_number,'string':args[2],'file':file_name}
        #print "'"+args[2]+"'",'encountered in',file_name,'at line',line_number
        sys.exit(2)
      head += tail[:m.start(1)] + str(n) + tail[m.end(1):m.end()]
      tail = tail[m.end():]
    ll = []
    p = 0
    while True :
      m = gv.newline_pat.search(tail,p)
      if not m : break
      p = m.end()
      ll.append (p)
    if len(ll) > 1 :
      pos = ll[-2]
      head = head + tail[:pos]
      tail = tail[pos:]
    head = ''

# The routines "insert", "remove", "switch" et al
# just receive an integer and return another integer.
def insert (n) :
  if n >= gv.number : return n+1
  return n

def check_before_remove (n) :
  if n == gv.number : return True
  return False

def remove (n) :
  assert n != gv.number
  if n > gv.number : return n-1
  return n

def switch (n) :
  if n == gv.number1 : return gv.number2
  if n == gv.number2 : return gv.number1
  return n

def commonprefix (list_of_paths):
  """Like in dospath, but more in the spirit of path manipulation.
  Items must end in os.sep if they represent directories."""
  number_of_paths = len(list_of_paths)
  if number_of_paths == 0: return ''
  first_path = list_of_paths[0]
  largest_i = -1
  for i in range(len(first_path)):
    stop = 0
    character = first_path[i]
    for n in range(1,number_of_paths):
      item = list_of_paths[n]
      if (i >= len(item)) or (character <> item[i]):
        # here we have used the fact that when the first condition
        # is true, python does not compute the second one
        stop = 1
        break
    if stop: break
    if character == os.sep: largest_i = i
  prefix = first_path[:largest_i+1]
  return prefix

#number_pat = re.compile ('[0-9]+')
gv.number_pat = re.compile ('\d+') # non-negative integer
action = args[1]
s = args[2]
if action in ['insert','remove','switch','switch-cond'] :
  white_pat = re.compile('\s+')
  head = ''
  tail = s
  while True :
    m = white_pat.search(tail)
    if not m : break
    head += re.escape(tail[:m.start()]) + '\s+'
    tail = tail[m.end():]
  s = head + re.escape(tail)
  p = 0
  while True :
    m = gv.number_pat.search(s,p)
    if not m : break
    keep_m = m
    p = m.end()
  if p == 0 :
    print 'string should contain a number'
    print
    usage()
  gv.number = int(keep_m.group())
  #s = re.escape(s[:m.start()]) + '[0-9]+' + re.escape(s[m.end():])
  s = s[:keep_m.start()] + '(\d+)' + s[keep_m.end():]
  gv.base_pat = re.compile (s)
  gv.newline_pat = re.compile (r'$\s',re.MULTILINE)
  tempfile.tempdir = commonprefix (args[-1])
  #tempfile.tempdir = commonprefix (list_of_files)
if action == 'insert' :
  list_of_files = args[3:]
  for file_name in list_of_files :
    engine (insert,file_name)
elif action == 'remove' :
  list_of_files = args[3:]
  gv.error_message = "'%(string)s' encountered in %(file)s at line %(line)d"
  for file_name in list_of_files :
    engine_ro (check_before_remove,file_name)
  for file_name in list_of_files :
    engine (remove,file_name)
elif action == 'switch':
  if len(gv.args) < 5 : usage ()
  gv.number1 = gv.number
  try : gv.number2 = int(args[3])
  except ValueError : usage ()
  list_of_files = args[4:]
  for file_name in list_of_files :
    engine (switch,file_name)
elif action == 'switch-cond' :  # !!
  print 'switch-cond action not yet implemented'
  sys.exit()
  list_of_files = args[8:]
  cond = args[6]
  if cond == '>' :
    for file_name in list_of_files :
      switch_gt(file_name,int(args[3]),int(args[4]), \
        re.compile(re.escape(args[5])),int(args[7]))
  elif cond == '<' :
    for file_name in list_of_files :
      switch_lt(file_name,int(args[3]),int(args[4]), \
        re.compile(re.escape(args[5])),int(args[7]))
  elif cond == '>=' :
    for file_name in list_of_files :
      switch_ge(file_name,int(args[3]),int(args[4]), \
        re.compile(re.escape(args[5])),int(args[7]))
  elif cond == '<=' :
    for file_name in list_of_files :
      switch_le(file_name,int(args[3]),int(args[4]), \
        re.compile(re.escape(args[5])),int(args[7]))
  else :
    print 'switch-cond: wrong condition', cond
    print
    usage()
elif action in ['about','version'] :
  print 'This is enum.py, version '+version+'.'
  print 'enum.py helps with automatic numbering of'
  print 'formulae, sections and theorems in documents.'
  print 'Copyright Cristian Barbarosie 2002-2017'
  print 'You may use and distribute freely this software'
  print 'under the terms of the GNU General Public License'
  print 'See http://www.gnu.org/copyleft/gpl.html'
  print 'This program comes with ABSOLUTELY NO WARRANTY;'
  print 'for details type : python enum.py warranty'
  print 'This is free software, and you are welcome to redistribute it'
  print 'under certain conditions; for details type : python enum.py copyright'
  print 'For examples of use, type : python enum.py usage'
elif action == 'warranty' :
  print 'There is no warranty for the program, to the extent permitted by'
  print 'applicable law. Except when otherwise stated in writing, the copyright holders'
  print 'and/or other parties provide the program "as is", without warranty of any kind,'
  print 'either expressed or implied, including, but not limited to, the implied'
  print 'warranties of merchantability and fitness for a particular purpose.'
  print 'The entire risk as to the quality and performance of the program is with you.'
  print 'Should the program prove deffective, you assume the cost of all necessary'
  print 'servicing, repair or correction.'
  print 'In no event, unless required by applicable law or agreed to in writing,'
  print 'will any copyright holder, or any other party who modifies and/or conveys'
  print 'the program as permitted by the GNU General Public License, be liable'
  print 'to you for any damages, including any general, special, incidental or'
  print 'consequential damages arising out of the use or inability to use the program' 
  print '(including, but not limited to, loss of data or data being rendered'
  print 'inaccurate or losses sustained by you or third parties or a failure of'
  print 'the program to operate with any other programs), even if such holder or'
  print 'other party has been advised of the possibility of such damages.'
elif action == 'copyright' :
  print 'This is enum.py, version '+version+'.'
  print 'enum.py helps with automatic numbering of'
  print 'formulae, sections and theorems in documents.'
  print 'Copyright Cristian Barbarosie 2002-2017'
  print 'You may use and distribute freely this software'
  print 'under the terms of the GNU General Public License.'
  print 'See http://www.gnu.org/copyleft/gpl.html'
  print 'You may convey verbatim copies of the program as you receive it,'
  print 'under the terms of section 4 of the GNU General Public License.'
  print 'You may convey a work based on the program, or the modifications'
  print 'to produce it from the program, under the terms of section 5 of'
  print 'the GNU General Public License.'
elif action in ['usage','help'] :
  usage(0)
  print
  print 'Read the user\'s manual at'
  print 'http://cristian-barbarosie.blogspot.com/p/english.html'
  print 'in the "Computers" section.'
else :
  print 'enum: wrong action'
  print
  usage()


