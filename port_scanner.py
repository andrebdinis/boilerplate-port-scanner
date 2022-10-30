import socket
from common_ports import * # to assign the service name to a port
import ipaddress # to validate ip address
from urllib.request import urlopen # to validate url
#import traceback # to print full traceback (if needed)

def get_open_ports(target, port_range, verbose=False):
  # "target" is URL or IP
  # "port_range" is list between two numbers '[1, 50]'
  # "verbose" is optional parameter with default value as 'False'
  print('##################### TEST ########################')
  print('TARGET: ', target)
  print('PORT_RANGE: ', port_range)
  print('VERBOSE: ', verbose)
  
  open_ports = []
  url = None
  ip = None
  hostname = None

  # Steps:

  # 1. validate "target" (URL or IP)
  # 1.0. Find out what to test first: the URL or the IP
  # 1.1. If URL invalid, then "Error: Invalid hostname"
  # 1.2. If IP invalid, then "Error: Invalid IP address"
  if target[:1].isalpha(): # test if first character is alphabet letter: [a-z]
    url = validateURL(target)
    if url:
      hostname = url.split('/')[2]
      try:
        ip = socket.gethostbyname(hostname)
      except Exception as e:
        print("Exception: Could not find IP address for hostname {}".format(hostname))
        return "Error: Invalid hostname"
    else:
      return "Error: Invalid hostname"
  elif target[:1].isnumeric(): # test if first character is numeric: [0-9]
    ip = validateIP(target)
    if ip:
      try:
        res = socket.gethostbyaddr(ip)
        if isinstance(res, tuple):
          url = res[0]
        else:
          url = res
        hostname = url.split('/')[2]
      except Exception as e:
        print("Exception: Could not find hostname for IP address {}".format(ip))
        #print(Exception, e)
    else:
      return "Error: Invalid IP address"
  else:
    return "Error: target is neither valid URL nor IP address"
  
  # 2. validate "port_range" (List of two numbers; 1st number must be <= than 2nd number)
  port_interval = validatePortRange(port_range)
  # 3. build list with open ports within the range
  # Internet Address Family:
  # 1. IPv4: socket.AF_INET
  # 2. IPv6: socket.AF_INET6
  # Socket Type:
  # 1. TCP: socket.SOCK_STREAM
  # 2. UDP: socket.SOCK_DGRAM
  #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # default: (IPv4, TCP)
  if url:
    if hostname:
      open_ports = portRangeScan(hostname, port_interval)
    else:
      open_ports = portRangeScan(url, port_interval)
  elif ip:
    open_ports = portRangeScan(ip, port_interval)
  else:
    return "Error: Neither url nor ip address were able to be tested"

  # 4. validate "verbose" (if set to True, then returns descriptive text)
  if verbose:
    if url and ip:
      if hostname:
        return getVerboseString(hostname, ip, open_ports)
      else:
        return getVerboseString(url, ip, open_ports)
    elif ip and not url:
      return getVerboseString('', ip, open_ports)
    else:
      return "?????????"
  else:
    return open_ports

############### AUXILIARY FUNCTIONS ###############

def validateIP(ip_string):
  try:
    ip_object = ipaddress.ip_address(ip_string)
    print("IP address '{ip_object}' valid".format(ip_object=ip_object))
    return ip_string
  except ValueError:
    print("IP address '{ip_string}' not valid".format(ip_string=ip_string))
    return False

def testURL(url_string):
  URL = url_string[:]
  error = None
  if not URL.startswith("http://") and not URL.startswith("https://"): error = True
  elif len(URL) == 0: error = True
  elif len(URL.split('/')) < 3: error = True
  if error: print('URL {} not valid'.format(URL)); return False
  print('URL {} valid'.format(URL))
  return URL

def addUrlSchemeIfMissing(url_string): # return list of 1 url (original) or 2 url's with scheme
  URL1 = None
  URL2 = None
  cond1 = not url_string.startswith("http://")
  cond2 = not url_string.startswith("https://")
  if (cond1 and cond2):
    URL1 = "https://" + url_string[:]
    URL2 = "http://" + url_string[:]
    return [URL1, URL2]
  else:
    URL1 = url_string[:]
    return [URL1]

def validateURL(url_string):
  URL_with_scheme = addUrlSchemeIfMissing(url_string)
  URL = testURL(URL_with_scheme[0])
  if URL: return URL
  if len(URL_with_scheme) == 2:
    URL = testURL(URL_with_scheme[1])
    if URL: return URL
  return False

def validatePortRange(port_range):
  try:
    cond1 = isinstance(port_range, list) # is list?
    cond2 = len(port_range) == 2 # has 2 elements?
    cond3 = isinstance(port_range[0], int) # is 1st number integer?
    cond4 = isinstance(port_range[1], int) # is 2nd number integer?
    if (cond1 and cond2 and cond3 and cond4):
      range = port_range.copy()
      range.sort()
      return range
    else:
      return False
      #print("Error: Port range input is invalid")
  except Error:
    return False

def portScan(host, port):
  try:
    #con = socketI.connect_ex((host, port))
    s = socket.socket()
    s.settimeout(0.5)
    con = s.connect_ex((host, port))
    if con:
      print("Port {port} is closed".format(port=port))
      s.close()
      return False
    else:
      print("Port {port} is OPEN".format(port=port))
      s.close()
      return True
  except Exception as e:
    print("Could not connect to port {port}".format(port=port))
    s.close()
    return False

def portRangeScan(host, port_range):
  min = port_range[0]
  max = port_range[1]
  port_list = range(min, max+1, 1)
  open_ports = list()
  for port in port_list:
    isOpenPort = portScan(host, port)
    if isOpenPort:
      open_ports.append(port)
  return open_ports

def getServiceNameByPort(port):
  service = ports_and_services.get(port)
  if not service: return ""
  else: return service

def justTitle(str_a):
  return str_a.ljust(9, " ")
  
def getVerboseString(url, ip, open_ports):
  verbose = ''
  title = 'Open ports for '
  subtitle = justTitle("PORT") + "SERVICE"
  if url and ip:
    title += "{URL} ({IP})".format(URL=url, IP=ip)
  elif ip and not url:
    title += "{IP}".format(IP=ip)
  else:
    raise Exception("not ip nor url????")
  verbose += title + "\n" + subtitle
  for port in open_ports:
    port_ljust = justTitle(str(port))
    service_name = getServiceNameByPort(port)
    verbose += "\n" + port_ljust + service_name
  print(verbose)
  return verbose




# URL BUGGED TESTING
def testURL_v1(url_string):
  URL = url_string[:]
  try:
    res = urlopen(URL)
    if res.status == 200 and res.msg == 'OK':
      print('URL {} is valid'.format(URL))
      return URL
    else:
      print('URL {} is not valid'.format(URL))
      return False
  except Exception as error:
    print('URL {} is not valid'.format(URL))
    return False
    #print(Exception, error)
    #traceback.print_exc() # print full stacktrace
    #traceback.format.exc() # return full stacktrace string
    #traceback.print_last()