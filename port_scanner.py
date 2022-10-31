import socket # look for open ports
from common_ports import * # assign the service name to a port
import ipaddress # validate ip address

# Get Open Ports function (parameters):
# - "target" is URL or IP
# - "port_range" is list between two numbers '[1, 50]'
# - "verbose" is optional parameter with default value as 'False'

def get_open_ports(target, port_range, verbose=False):
  printGetOpenPortsInputLegend(target, port_range, verbose)
  
  open_ports = []
  url = None
  ip = None
  hostname = None

  # 1. validate "target" (try to get URL, IP and Hostname)
  # 1.1. If URL invalid, then "Error: Invalid hostname"
  # 1.2. If IP invalid, then "Error: Invalid IP address"
  data = validateTarget(target)
  if isinstance(data, str): return data
  else:
    url, ip, hostname = [data[i] for i in (0, 1, 2)]

  # 2. validate "port_range" (list of two numbers: 1st number must be <= 2nd number)
  port_interval = validatePortRange(port_range)
  
  # 3. build list with open ports within the specified range
  if url and hostname:
    open_ports = portRangeScan(hostname, port_interval)
  else:
    open_ports = portRangeScan(ip, port_interval)

  # 4. validate "verbose" (if 'True', then returns descriptive text)
  if verbose:
    if url and hostname:
      return getVerboseString(hostname, ip, open_ports)
    else:
      return getVerboseString('', ip, open_ports)
  else:
    return open_ports

############### AUXILIARY FUNCTIONS ###############

# Print Input
def printGetOpenPortsInputLegend(target, port_range, verbose):
  target_spacing = len(target) + 4
  port_range_spacing = len(str(port_range)) + 4
  verbose_spacing = 7
  total = (target_spacing + port_range_spacing + verbose_spacing) + 4
  print('|' + ' INPUT '.center(total, "-"))
  print('|' + ' TARGET'.ljust(target_spacing) + 'PORT_RANGE'.ljust(port_range_spacing) + 'VERBOSE'.ljust(verbose_spacing))
  print('|' + (' '+target).ljust(target_spacing) + str(port_range).ljust(port_range_spacing) + str(verbose).ljust(verbose_spacing))
  print('|' + "-".center(total, "-"))

# Validation
def validateIP(ip_string):
  try:
    ip_object = ipaddress.ip_address(ip_string)
    print("IP address '{ip_object}' VALID".format(ip_object=ip_object))
    return ip_string
  except ValueError:
    print("IP address '{ip_string}' not valid".format(ip_string=ip_string))
    return False

def validateUrlFormat(url_string):
  URL = url_string[:]
  #if not URL.startswith("http://") and not URL.startswith("https://"): error = True
  if (len(URL) == 0) or (len(URL.split('/')) < 3):
    print('URL {} format not valid'.format(URL))
    return False
  else:
    print('URL {} format VALID'.format(URL))
    return URL

def addUrlSchemeIfMissing(url_string): # return list of 1 url (original) or 2 url's with scheme
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
  URL = validateUrlFormat(URL_with_scheme[0])
  if URL: return URL
  if len(URL_with_scheme) == 2:
    URL = validateUrlFormat(URL_with_scheme[1])
    if URL: return URL
  return False

def validateTarget(target):
  if target[:1].isalpha(): # test if first character is alphabet letter: [a-z]
    url = validateURL(target)
    if url:
      hostname = url.split('/')[2]
      try:
        ip = socket.gethostbyname(hostname)
        return [url, ip, hostname]
      except Exception as e:
        print("Exception: Could not find IP address for hostname {}".format(hostname))
        print("Error: Invalid hostname")
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
          hostname = url
        else:
          url = res
          hostname = url.split('/')[2]
        return [url, ip, hostname]
      except Exception as e:
        print("Exception: Could not find hostname for IP address {}".format(ip))
        return [None, ip, None]
    else:
      return "Error: Invalid IP address"
  else:
    return "Error: target is neither valid URL nor IP address"

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


# Port Scan
def portScan(host, port):
  # socket.socket(internet_address_family, socket_type):
  # - Internet Address Family: (IPv4: socket.AF_INET | IPv6: socket.AF_INET6)
  # - Socket Type: (TCP: socket.SOCK_STREAM | UDP: socket.SOCK_DGRAM)
  try:    
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # means (IPv4, TCP)
    s = socket.socket() # this code is equal to the line above:
    s.settimeout(0.25)
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


# Verbose
def getServiceNameByPort(port):
  service = ports_and_services.get(port)
  if not service: return ""
  else: return service

def justifyTitle(str_a):
  return str_a.ljust(9, " ")
  
def getVerboseString(url, ip, open_ports):
  verbose = ''
  title = 'Open ports for '
  subtitle = justifyTitle("PORT") + "SERVICE"
  if url and ip:
    title += "{URL} ({IP})".format(URL=url, IP=ip)
  else:
    title += "{IP}".format(IP=ip)
  verbose += title + "\n" + subtitle
  for port in open_ports:
    port_ljust = justifyTitle(str(port))
    service_name = getServiceNameByPort(port)
    verbose += "\n" + port_ljust + service_name
  print(verbose)
  return verbose
