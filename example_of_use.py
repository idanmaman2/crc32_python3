import rcrc32 
rcrc32.init_tables()
code =0x176829F8
print("result :" , rcrc32.findReverse(0x176829F8) ) 
print("verfication : " , 0x176829F8 == rcrc32.calc(b"7hbd") ) 