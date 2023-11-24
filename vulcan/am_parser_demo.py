import json
from argparse import ArgumentParser

import penman

from vulcan.server.basic_layout import BasicLayout
from vulcan.server.server import Server
from vulcan.data_handling.data_corpus import from_dict_list
from vulcan.data_handling.format_names import FORMAT_NAME_STRING, FORMAT_NAME_GRAPH

input_dict = json.loads(
    """{"errors": [], "sentence": "the boy wants to sleep.", "parses": {"AMR-2017": {"amdep": "#raw:the boy wants to sleep.\\n#batch_size:1\\n#normalized_nn_time:0.3039579391479492\\n#normalized_prepare_ftd_time:0.0023775100708007812\\n#host:jones-6\\n#parser:ftd\\n#parsing_time:0.003675222396850586\\n#k-supertags:6\\n1\\tthe\\t_\\tthe\\tDT\\tO\\t_\\t$LEMMA$\\t_\\t0\\tIGNORE\\tTrue\\n2\\tboy\\t_\\tboy\\tNN\\tO\\t(d<root> / --LEX--)\\t$LEMMA$\\t()\\t3\\tAPP_s\\tTrue\\n3\\twants\\t_\\twant\\tVBZ\\tO\\t(c<root> / --LEX--  :ARG0 (y<s>)  :ARG1 (m<o>))\\t$LEMMA$-01\\t(o(s()))\\t0\\tROOT\\tTrue\\n4\\tto\\t_\\tto\\tTO\\tO\\t_\\tcause-01\\t_\\t0\\tIGNORE\\tTrue\\n5\\tsleep\\t_\\tsleep\\tVB\\tO\\t(s<root> / --LEX--  :ARG0 (y<s>))\\t$LEMMA$-01\\t(s())\\t3\\tAPP_o\\tTrue\\n6\\t.\\t_\\t.\\t.\\tO\\t_\\t$LEMMA$\\t_\\t0\\tIGNORE\\tTrue\\n\\n", "parse_time": 0.34325146675109863, "penman": "(u_2 / want-01  :ARG0 (u_3 / boy  :ARG0-of (u_1 / sleep-01  :ARG1-of u_2)))\\n\\n", "postprocess_time": 0.3073859214782715}, "EDS": {"amdep": "#raw:the boy wants to sleep.\\n#batch_size:1\\n#normalized_nn_time:0.4693145751953125\\n#normalized_prepare_ftd_time:0.0019643306732177734\\n#host:jones-6\\n#parser:ftd\\n#parsing_time:0.003276824951171875\\n#k-supertags:6\\n1\\tthe\\t_\\tthe\\tDT\\tO\\t(explicitanon_5<root> / --LEX--  :lnk (explicitanon_u_205454 / SIMPLE)  :BV (x27<det>))\\t_$LEMMA$_q\\t(det())\\t2\\tMOD_det\\tTrue\\n2\\tboy\\t_\\tboy\\tNN\\tO\\t(x6<root> / --LEX--  :lnk (explicitanon_u_442034 / SIMPLE))\\t_$LEMMA$_n_1\\t()\\t3\\tAPP_s\\tTrue\\n3\\twants\\t_\\twant\\tVBZ\\tO\\t(e3<root> / --LEX--  :lnk (explicitanon_u_510816 / SIMPLE)  :ARG2 (e12<o>)  :ARG1 (x5<s>))\\t_$LEMMA$_v_1\\t(o(s()))\\t0\\tROOT\\tTrue\\n4\\tto\\t_\\tto\\tTO\\tO\\t_\\t_\\t_\\t0\\tIGNORE\\tTrue\\n5\\tsleep\\t_\\tsleep\\tVB\\tO\\t(e5<root> / --LEX--  :lnk (explicitanon_u_554027 / SIMPLE)  :ARG1 (e3<s>))\\t_$LEMMA$_v_1\\t(s())\\t3\\tAPP_o\\tTrue\\n6\\t.\\t_\\t.\\t.\\tO\\t_\\t_\\t_\\t0\\tIGNORE\\tTrue\\n\\n", "parse_time": 0.49014711380004883, "penman": "(u_4 / _want_v_1  :ARG2 (e5 / _sleep_v_1  :ARG1 (x6 / _boy_n_1  :BV-of (explicitanon_5 / _the_q)  :ARG1-of u_4)))\\n\\n", "postprocess_time": 0.10121750831604004}, "DM": {"amdep": "#raw:the boy wants to sleep.\\n#batch_size:1\\n#normalized_nn_time:0.32946062088012695\\n#normalized_prepare_ftd_time:0.003437519073486328\\n#host:jones-6\\n#parser:ftd\\n#parsing_time:0.011902093887329102\\n#k-supertags:6\\n1\\tthe\\t_\\tthe\\tDT\\tO\\t(i_4<root> / --LEX--  :BV (i_6<det>))\\t~~q:i-h-h\\t(det())\\t2\\tMOD_det\\tTrue\\n2\\tboy\\t_\\tboy\\tNN\\tO\\t(i_2<root> / --LEX--)\\t~~n:x\\t()\\t3\\tAPP_s\\tTrue\\n3\\twants\\t_\\twant\\tVBZ\\tO\\t(i_4<root> / --LEX--  :ARG1 (i_2<s>)  :ARG2 (i_6<o>))\\t~~v:e-i-h\\t(o(s()))\\t7\\tAPP_art-snt1\\tTrue\\n4\\tto\\t_\\tto\\tTO\\tO\\t_\\t_\\t_\\t0\\tIGNORE\\tTrue\\n5\\tsleep\\t_\\tsleep\\tVB\\tO\\t(i_3<root> / --LEX--  :ARG1 (i_2<s>))\\t~~v:e-i\\t(s())\\t3\\tAPP_o\\tTrue\\n6\\t.\\t_\\t.\\t.\\tO\\t_\\t_\\t_\\t0\\tIGNORE\\tTrue\\n7\\tART-ROOT\\t_\\tART-ROOT\\tART-ROOT\\tART-ROOT\\t(ART-ROOT<root> / --LEX--  :art-snt1 (i_2<art-snt1>))\\t$LEMMA$\\t(art-snt1())\\t0\\tROOT\\tTrue\\n\\n", "parse_time": 0.3663821220397949, "sdp": "#SDP 2015\\n#NO-ID\\n1\\tthe\\tthe\\tDT\\t-\\t+\\tq:i-h-h\\t_\\t_\\t_\\n2\\tboy\\tboy\\tNN\\t-\\t-\\tn:x\\tBV\\tARG1\\tARG1\\n3\\twants\\twant\\tVBZ\\t+\\t+\\tv:e-i-h\\t_\\t_\\t_\\n4\\tto\\tto\\tTO\\t-\\t-\\t_\\t_\\t_\\t_\\n5\\tsleep\\tsleep\\tVB\\t-\\t+\\tv:e-i\\t_\\tARG2\\t_\\n6\\t.\\t.\\t.\\t-\\t-\\t_\\t_\\t_\\t_\\n\\n", "postprocess_time": 1.1191236972808838}}}""")


# print(layout.layout)
def request_data_to_layout(request_data):
    # TODO run parser on request data to give an input_dict
    print(request_data)
    return BasicLayout.from_am_parser_dict(input_dict)


def main():
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", type=int, action="store", dest="port", default=5050,
                        help="Specify the port to use for this visualization.")
    # parser.add_argument("-pf", "--propbank-frames", type=str,
    #                     action="store", dest="propbank_frames", default=None,
    #                     help="Path to a folder containing XML files with Propbank frames, "
    #                          "such as data/frames/propbank-amr-frames-xml-2018-01-25 in the AMR3.0 corpus. "
    #                          "If given, vulcan will show frame definitions on node mouseover ")
    # parser.add_argument("-wiki", "--show-wikipedia-articles", action="store_true", dest="show_wikipedia_articles",
    #                     default=False, help="If given, vulcan will show Wikipedia articles on node mouseover."
    #                                         "Can take quite a while to load in the beginning!")
    args = parser.parse_args()



    # layout is python object containing the trees, graphs etc we want to visualize
    server = Server(lambda input_data: request_data_to_layout(input_data), port=args.port)
    server.start()  # at this point, the server is running on this thread, and nothing below will be executed


if __name__ == '__main__':
    main()

