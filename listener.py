"""

Baato
    Copyright (C) 2015 Rohan Verma

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""


import select, socket
import time
import thread
from flask import Flask, render_template

ONLINE_LIST = []
ONLINE_IP_LIST =[]
RESET = 1

MYPORT = 50000

def broadcast_query():

	global RESET
	if(RESET == 0):
		time.sleep(15*60)
		RESET = 1
	RESET = 1
	query = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	query.bind(('', 0))
	query.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	data = 'QUERY'
	query.sendto(data, ('<broadcast>', MYPORT))
	print "Sent Refresh QUERY"

def listener_thread():

	global ONLINE_LIST
	global ONLINE_IP_LIST
	global RESET

	bufferSize = 1024 # whatever you need

	#BROADCAST = '10.6.15.255'
	MYPORT = 50000

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	s.bind(('<broadcast>', MYPORT))
	s.setblocking(0)


	while True:
	    result = select.select([s],[],[])
	    msg = result[0][0].recv(bufferSize) 

	    if(RESET == 1):
	    	ONLINE_LIST = []
	    	ONLINE_IP_LIST = []
	    	RESET = 0

	    if(msg != "QUERY"):
		    status = msg.split(';')[0]
		    ip = msg.split(';')[1]
		    name = msg.split(';')[2]
		    #print name
		    if(status == "ONLINE"):
		    	if(ip not in ONLINE_IP_LIST):
		    		ONLINE_LIST.append([ip,name])
		    		ONLINE_IP_LIST.append(ip)
		    if(status == "CLOSED"):
		    	if(ip in ONLINE_IP_LIST):
		    		ONLINE_LIST.remove([ip,name])
		    		ONLINE_IP_LIST.remove(ip)
		    if(status == "STARTED"):
		    	if(ip not in ONLINE_IP_LIST):
		    		ONLINE_LIST.append([ip,name])
		    		ONLINE_IP_LIST.append(ip)


app = Flask(__name__)

@app.route('/')
def display():
	return render_template('index.html', online=ONLINE_LIST)


if __name__ == '__main__':
	thread.start_new_thread(listener_thread, ())
	thread.start_new_thread(broadcast_query, ())
	#app.run(debug=True)
	app.run(host='0.0.0.0')