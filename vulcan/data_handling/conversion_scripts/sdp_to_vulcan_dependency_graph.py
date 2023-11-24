

example = """#SDP 2015
#NO-ID
1	the	the	DT	-	+	q:i-h-h	_	_	_
2	boy	boy	NN	-	-	n:x	BV	ARG1	ARG1
3	wants	want	VBZ	+	+	v:e-i-h	_	_	_
4	to	to	TO	-	-	_	_	_	_
5	sleep	sleep	VB	-	+	v:e-i	_	ARG2	_
6	.	.	.	-	-	_	_	_	_

"""


def sdp_to_vulcan_dependency_graph(sdp_string):
    
    for line in sdp_string.split("\n"):
        if line.startswith("#"):
            continue
        if line.strip() == "":
            continue
        parts = line.split("\t")
        print(parts)


def main():
    sdp_to_vulcan_dependency_graph(example)


if __name__ == '__main__':
    main()

