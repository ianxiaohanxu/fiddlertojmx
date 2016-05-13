import simplejson as json
import sys, os, re
_indent = "  "
assert len(sys.argv[1:])==1, "The script need on json file as argument."

with open(sys.argv[1], "r") as fb:
    in_json = json.load(fb)

api_list = in_json["log"]["entries"]
api_request_list = [item["request"] for item in api_list]
_head_HTTPSamplerProxy = '<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="%s" enabled="true">\n'
_tail_HTTPSamplerProxy = "</HTTPSamplerProxy>\n"
_head_hashTree = "<hashTree>\n"
_tail_hashTree = "</hashTree>\n"
_empty_hasTree = "<hashTree/>\n"
_head_HeaderManager = '<HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="HTTP Header Manager" enabled="true">'
_tail_HeaderManager = "</HeaderManager>"
_head_long_elementProp = '<elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" enabled="true">\n'
_head_short_elementProp = '<elementProp name="%s" elementType="%s">\n'
_tail_elementProp = '</elementProp>\n'
_head_collectionProp = '<collectionProp name="%s">\n'
_tail_collectionProp = '</collectionProp>\n'
_empty_collectionProp = '<collectionProp name="Arguments.arguments"/>\n'
_boolProp = '<boolProp name="%s">%s</boolProp>\n'
_stringProp = '<stringProp name="%s">%s</stringProp>\n'

output_string = ""
def replace_special(in_str):
    in_str = in_str.replace("&", "&amp;")
    in_str = in_str.replace("<", "&lt;")
    in_str = in_str.replace(">", "&gt;")
    in_str = in_str.replace('"', "&quot;")
    return in_str

def parse_url(api):
    if len(api["queryString"])>0 and api["method"]=="GET":
        url = api["url"].split("?")[0]
    else:
        url = api["url"]
    url = replace_special(url)
    r = re.compile(r"(?<!/)/(?!/)")
    try:
        host, uri = r.split(url, maxsplit=1)
    except:
        host = url
        uri = ""
    uri = "/" + uri
    r = re.compile(r".*:\d{4}$")
    if r.match(host):
        port = host[-4:]
        host = host[:-5]
        protocol, host = host.split("//")
        protocol = protocol[:-1]
    else:
        port = ""
        protocol, host = host.split("//")
        protocol = protocol[:-1]
    return protocol, host, port, uri

_counter = 1
for api in api_request_list:
    protocol, host, port, uri = parse_url(api)
    _testname = str(_counter) + " " + uri
    _counter += 1
    output_string += _head_HTTPSamplerProxy %_testname
    if api["method"] in ("POST", "PUT", "PATCH"):
        output_string += _boolProp %("HTTPSampler.postBodyRaw", "true")
        output_string += _head_short_elementProp %("HTTPsampler.Arguments", "Arguments")
        output_string += _head_collectionProp %"Arguments.arguments"
        output_string += _head_short_elementProp %("", "HTTPArgument")
        output_string += _boolProp %("HTTPArgument.always_encode", "false")
        request_text = replace_special(api["postData"]["text"])
        output_string += _stringProp %("Argument.value", request_text)
        output_string += _stringProp %("Argument.metadata", "=")
        output_string += _tail_elementProp
        output_string += _tail_collectionProp
        output_string += _tail_elementProp
    elif api["method"] in ("GET", "DELETE"):
        output_string += _head_long_elementProp
        if len(api["queryString"])==0:
            output_string += _empty_collectionProp
        else:
            output_string += _head_collectionProp %"Arguments.arguments"
            for query_str in api["queryString"]:
                output_string += _head_short_elementProp %(query_str["name"], "HTTPArgument")
                output_string += _boolProp %("HTTPArgument.always_encode", "false")
                output_string += _stringProp %("Argument.name", query_str["name"])
                output_string += _stringProp %("Argument.value", replace_special(query_str["value"]))
                output_string += _stringProp %("Argument.metadata", "=")
                output_string += _tail_elementProp
            output_string += _tail_collectionProp
        output_string += _tail_elementProp
    output_string += _stringProp %("HTTPSampler.domain", host)
    output_string += _stringProp %("HTTPSampler.port", port)
    output_string += _stringProp %("HTTPSampler.connect_timeout", "")
    output_string += _stringProp %("HTTPSampler.response_timeout", "")
    output_string += _stringProp %("HTTPSampler.protocol", protocol)
    output_string += _stringProp %("HTTPSampler.contentEncoding", "")
    output_string += _stringProp %("HTTPSampler.path", uri)
    output_string += _stringProp %("HTTPSampler.method", api["method"])
    output_string += _boolProp %("HTTPSampler.follow_redirects", "true")
    output_string += _boolProp %("HTTPSampler.auto_redirects", "false")
    output_string += _boolProp %("HTTPSampler.use_keepalive", "true")
    output_string += _boolProp %("HTTPSampler.DO_MULTIPART_POST", "false")
    output_string += _boolProp %("HTTPSampler.monitor", "false")
    output_string += _stringProp %("HTTPSampler.embedded_url_re", "")
    output_string += _tail_HTTPSamplerProxy
    output_string += _head_hashTree
    output_string += _head_HeaderManager
    output_string += _head_collectionProp %"HeaderManager.headers"
    for header in api["headers"]:
        output_string += _head_short_elementProp %(header["name"], "Header")
        output_string += _stringProp %("Header.name", header["name"])
        output_string += _stringProp %("Header.value", replace_special(header["value"]))
        output_string += _tail_elementProp
    output_string += _tail_collectionProp
    output_string += _tail_HeaderManager
    output_string += _empty_hasTree
    output_string += _tail_hashTree

with open("jmeter_head.xml", "r") as fb:
    jmeter_head = fb.read()

jmeter_tail = _tail_hashTree * 4 + "</jmeterTestPlan>"
jmeter_string = jmeter_head + output_string + jmeter_tail

with open("exported_jmeter.jmx", "w") as fb:
    fb.write(jmeter_string)




