import sys
from pprint import pprint

line_counter = 1

class Statement:

	def __init__(self, input, follows_from, rule, subproof):

		global line_counter

		self.string = input
		self.follows_from = follows_from
		self.line_num =  line_counter
		self.rule = rule
		self.subproof = subproof

		line_counter += 1



class Proof:

	
	conclusion = ""
	knowledge_base = []
	
	def __init__(self, filename):
		global line_counter
		file = open(filename, encoding="utf-8")
		filetype = -1
		if (filename[-4:] == ".txt"):
			filetype = 0
		elif (filename[-5:] == ".bram"):
			filetype = 1
		else:
			print("ERROR: Unrecognized file type")
			sys.exit()
		for line in file:
			line = line.strip()
			if (filetype):
				if (line[0:5] == "<raw>"):
					# Take off tags
					line = line[5:-6]
					# Take out comments
					if ('#' in line):
						line = line[0:line.find('#')]
					# Convert symbols
					line = line.replace('∧', '&')	# And
					line = line.replace('∨', '|')	# Or
					line = line.replace('¬', '~')	# Not
					statement = Statement(line, "NULL", "NULL", 0)
					self.knowledge_base.append(statement)
			else:
				statement = Statement(line, "NULL", "NULL", 0)
				self.knowledge_base.append(statement)
		self.conclusion = self.knowledge_base[-1].string
		self.knowledge_base.pop(-1)
		self.nextPid = 0 #for .bram conversion
		line_counter -= 1

	def initial_expand(self):
		neg_conc = "~"+self.conclusion
		statement = Statement(neg_conc, "NULL", "NULL", 1)
		self.knowledge_base.append(statement)

		if neg_conc[0:2] == "~~":
			statement2 = Statement(neg_conc[2:], "{"+str(statement.line_num)+"}", "\lnote", 1)
			self.knowledge_base.append(statement2)
		new = []
		for item in self.knowledge_base:
			if "&" in item.string:
				new_items = item.string.split("&")
				new_cleaned = []
				for new_item in new_items:
					new_item = new_item.strip(" ").replace("(","").replace(")","")

					statement = Statement(new_item, "{"+str(item.line_num)+"}", "\lande", 1)
					new.append(statement)
		for item in new:
			self.knowledge_base.append(item)



	def search_kb(self, base, look_for):
		for item in base[::-1]:
			if item.string == look_for:
				return item.line_num
		return False

	def search_or_elim(self, subproofs):
		set_list = []
		for subproof in subproofs:
			myset = set()
			for item in subproof:
				myset.add(item.string)
			set_list.append(myset)
		newset = set_list[0]

		for s in set_list:
			newset &= s
		if "!" in newset:
			newset = set(["!"])
		return newset



	def breakdown_or(self):


		for item in self.knowledge_base:
			if "&" in item.string:
				continue
			item.string = item.string.replace("(","").replace(")","")

			new = []

			if "|" in item.string:
				subproofs = []
				split = item.string.split("|")
				for sub in split:

					sub = sub.strip(" ")
					subproof = []
					new_clause = sub.strip(" ")
					statement = Statement(new_clause, "NULL", "NULL", 2)
					subproof.append(statement)
					if new_clause[0] == "~":
						search = self.search_kb(self.knowledge_base, new_clause[1:])
					else:
						search = self.search_kb(self.knowledge_base, "~"+new_clause)

					if search != False:
						statement2 = Statement("!", "{"+str(statement.line_num)+"}{"+str(search)+"}", "\lfalsei", 2)
						subproof.append(statement2)
						for sta in split:
							sta = sta.strip(" ")
							if sta != sub:
								statement3 = Statement(sta, "{"+str(statement2.line_num)+"}", "\lfalsee", 2)
								subproof.append(statement3)
					else:
						statement2 = Statement(statement.string, "{"+str(statement.line_num)+"}", "\\reit", 2)
						subproof.append(statement2)
					subproofs.append(subproof)


				clause = self.search_or_elim(subproofs)
				if len(clause) == 1:
					line = ""
					for sub in subproofs:
						line += "{"
						line += str(sub[0].line_num)
						line += "--"
						line += str(sub[-1].line_num)
						line += "}"

						for state in sub:
							self.knowledge_base.append(state)

					line += "{"
					line += str(item.line_num)
					line += "}"
					statement = Statement(clause.pop(), line, "\lore", 1)
					self.knowledge_base.append(statement)



	def gen_conclusion(self):
		sub_start = None
		for line in self.knowledge_base:
			if line.string == "!" and line.subproof == 1:
				for line2 in self.knowledge_base:
					if line2.subproof == 1:
						sub_start = line2
						break
				statement = Statement("~"+sub_start.string, "{"+str(sub_start.line_num)+"--"+str(self.knowledge_base[-1].line_num)+"}", "\lnoti", 0)
				self.knowledge_base.append(statement)
				if statement.string[0:2] == "~~":
					statement = Statement(statement.string[2:], "{"+str(statement.line_num)+"}", "\lnote", 0)
					self.knowledge_base.append(statement)
				return True
		return False

	def rule_to_bram(self, rule):
		rules = {"\\lnote": "DOUBLENEGATION", "\\lande": "SIMPLIFICATION", "\\lfalsei": "CONTRADICTION", "\\lfalsee": "PRINCIPLE_OF_EXPLOSION", "\\reit": "REITERATION", "\\lore": "DISJUNCTIVE_SYLLOGISM", "\\lnoti": "PROOF_BY_CONTRADICTION"}
		return rules[rule]

	def follows_to_bram(self, follows):
		follows = [f.strip("}") for f in follows.split("{") if f != ""]
		follows = [int(f.split("-")[0]) - 1 for f in follows]
		return sorted(follows)

	def line_to_bram(self, line):
		line = line.replace("|","∨")
		line = line.replace("&","∧")
		line = line.replace("~","¬")
		line = line.replace("!","⊥")
		line = line.split() # may be able to get rid of
		line = "".join(line)
		return line

	def proof_to_bram(self, num, n, pid, prev_level):
		self.nextPid += 1
		orign = n # if subroofs exist, pass this in
		r = [] # current proof
		proofs = [r]
		def rwrite(s):
			#nonlocal r
			#nonlocal n
			r.append("{}{}\n".format(n * 2 * ' ', s))

		rwrite('<proof id="{}">'.format(pid))
		n += 1

		# write premises
		if pid == 0: #multiple premises can exist on outer level
			for line in self.knowledge_base:
				if line.subproof > 0: # CAN CHANGE WAY PREMISES ARE DETECTED IN FUTURE
					break
				rwrite('<assumption linenum="{}">'.format(num))
				n += 1
				outstring = self.line_to_bram(line.string)
				rwrite("<raw>{}</raw>".format(outstring))
				n -= 1
				rwrite("</assumption>")
				num += 1

		else: # only one premise in subproof
			line = self.knowledge_base[num]
			rwrite('<assumption linenum="{}">'.format(num))
			n += 1
			outstring = self.line_to_bram(line.string)
			rwrite("<raw>{}</raw>".format(outstring))
			n -= 1
			rwrite("</assumption>")
			num += 1

		i = num
		while i < len(self.knowledge_base):
			line = self.knowledge_base[i].string
			if self.knowledge_base[i].subproof > prev_level: # start of subproof
				rwrite('<step linenum="{}">'.format(i))
				n += 1
				rwrite("<rule>SUBPROOF</rule>")
				rwrite("<premise>{}</premise>".format(self.nextPid))
				n -= 1
				rwrite("</step>")
				subproof, i = self.proof_to_bram(i, orign, self.nextPid, prev_level + 1)
				proofs.extend(subproof)
			elif self.knowledge_base[i].subproof < prev_level: # end of subproof
				break
			elif self.knowledge_base[i].rule == "NULL": # start of subproof immediately after end of subproof
				break
			else:
				rwrite('<step linenum="{}">'.format(i))
				n += 1
				rwrite("<raw>{}</raw>".format(self.line_to_bram(line)))
				rwrite("<rule>{}</rule>".format(self.rule_to_bram(self.knowledge_base[i].rule))) # FIX
				# rwrite("<rule/>") # FIX
				for p in self.follows_to_bram(self.knowledge_base[i].follows_from):
					rwrite("<premise>{}</premise>".format(p)) # FIX
				n -= 1
				rwrite("</step>")

				i += 1

		# goal
		if pid == 0:
			outstring = self.line_to_bram(self.conclusion)	
			rwrite("<goal>")
			n += 1
			rwrite("<raw>{}</raw>".format(outstring))
			n -= 1
			rwrite("</goal>")

		n -= 1
		rwrite("</proof>")

		proofs[0] = "".join(proofs[0]) # convert to string
		return proofs, i

	def to_bram_file(self):
		num = 0

		n = 0
		f = open("output.bram","w", encoding="utf-8")
		def swrite(s):
			#nonlocal n
			#nonlocal f
			f.write("{}{}\n".format(n * 2 * ' ', s))
		
		swrite('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
		swrite("<bram>")
		n += 1
		# swrite("<program>python-ND-APG</program>")
		swrite("<program>Aris</program>")
		swrite("<version>1.0</version>")
		swrite("<metadata>")
		n += 1
		swrite("<author>UNKNOWN</author>")
		n -= 1
		swrite("</metadata>")
		proofs = self.proof_to_bram(num, n, 0, 0)[0]
		for proof in proofs:
			f.write(proof)

		n -= 1
		swrite("</bram>")

	
	def line_to_tex(self, line):
		line = line.replace("|","\lor ")
		line = line.replace("&","\land ")
		line = line.replace("~","\lnot ")
		line = line.replace("!","\lfalse ")
		return line
		
	def to_tex_file(self):
		num = 0
		f = open("output.tex","w")
		f.write("\documentclass{article}\n")
		f.write("\\usepackage{lplfitch}\n")
		f.write("\\")
		f.write("begin{document}\n")
		premise_string = "\\fitchprf{"
		for line in self.knowledge_base:
			if line.subproof >0:
				break
			outstring = self.line_to_tex(line.string)
			if num > 0:
				premise_string += "\\\\"
				premise_string += "\n"
			premise_string += "\pline["+str(line.line_num)+".]{"
			premise_string += outstring
			premise_string += "}"
			num += 1

		f.write(premise_string+"}\n{")

		prev_level = 0
		pline = False
		for i in range(num,len(self.knowledge_base)):
			line = self.knowledge_base[i].string
			if self.knowledge_base[i].subproof > prev_level:
				if pline:
					f.write("\\\\")
				f.write("\n\subproof{\pline["+str(self.knowledge_base[i].line_num)+".]{"+self.line_to_tex(line)+"}}\n{")
				prev_level += 1
				pline = False
			elif self.knowledge_base[i].subproof < prev_level:
				f.write("\n}\n")
				f.write("\pline["+str(self.knowledge_base[i].line_num)+".]{"+self.line_to_tex(line)+"}["+self.knowledge_base[i].rule+self.knowledge_base[i].follows_from+"]")
				prev_level -= 1
				pline = True
			elif self.knowledge_base[i].rule == "NULL":

				f.write("\n}\n")
				f.write("\subproof{\pline["+str(self.knowledge_base[i].line_num)+".]{"+self.line_to_tex(line)+"}}\n{")
				pline = False
			else:
				if pline:
					f.write("\\\\")
				f.write("\n\pline["+str(self.knowledge_base[i].line_num)+".]{"+self.line_to_tex(line)+"}["+self.knowledge_base[i].rule+self.knowledge_base[i].follows_from+"]")
				pline = True
		f.write("}")
		f.write("\n\end{document}")

		





if __name__ == "__main__":
	try:
		open(sys.argv[1])
	except FileNotFoundError:
		print("ERROR: could not open", sys.argv[1])
		sys.exit()

	proof = Proof(sys.argv[1])

	proof.initial_expand()
	proof.breakdown_or()
	if not proof.gen_conclusion():
		print("ERROR: Could not resolve given premises and conclusion")
		sys.exit()

	if len(sys.argv) == 3 and sys.argv[2] == "latex":
		proof.to_tex_file()
	else:
		proof.to_bram_file()
	
	