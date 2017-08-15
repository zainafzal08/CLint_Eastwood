
			if curr.lower() == "/" and stream.peek() == "/":
				curr = self.LL1SkipUntil(stream,"",'\n')
				return Token("comment",curr,stream.currLine,stream.lineIndex)
			if curr.lower() == "/" and stream.peek() == "*":
				stream.getNext() # skip the '*'s
				curr = self.LL2SkipUntil(stream,"",'*','/')

				return Token("comment",curr,stream.currLine,stream.lineIndex)
			
			# expressions
			if curr.lower() == "=" and stream.peek() == "=":
				curr += stream.getNext()
				return Token("mathSymbol",curr,stream.currLine,stream.lineIndex)
			elif curr.lower() == "=":
				return Token("equals",curr,stream.currLine,stream.lineIndex)

							if curr == '"':
				curr = self.LL1SkipUntil(stream,curr,'"')
				return Token("stringLiteral",curr,stream.currLine,stream.lineIndex)

			if re.match(r'\'[^\']\'',curr):
				return Token("charLiteral",curr,stream.currLine,stream.lineIndex)