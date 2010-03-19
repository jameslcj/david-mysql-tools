#encoding=utf-8
INNODB_PAGE_SIZE = 16*1024*1024

# Start of the data on the page
FIL_PAGE_DATA = 38


FIL_PAGE_OFFSET = 4 # page offset inside space
FIL_PAGE_TYPE = 24 # File page type

# Types of an undo log segment */
TRX_UNDO_INSERT = 1
TRX_UNDO_UPDATE = 2

# On a page of any file segment, data may be put starting from this offset
FSEG_PAGE_DATA = FIL_PAGE_DATA

# The offset of the undo log page header on pages of the undo log
TRX_UNDO_PAGE_HDR = FSEG_PAGE_DATA

PAGE_LEVEL = 26	#level of the node in an index tree; the leaf level is the level 0 */
				
innodb_page_type={
	'0000':u'Freshly Allocated Page',
	'0002':u'Undo Log Page',
	'0003':u'File Segment inode',
	'0004':u'Insert Buffer Free List',
	'0005':u'Insert Buffer Bitmap',
	'0006':u'System Page',
	'0007':u'Transaction system Page',
	'0008':u'File Space Header',
	'0009':u'扩展描述页',
	'000a':u'Uncompressed BLOB Page',
	'000b':u'1st compressed BLOB Page',
	'000c':u'Subsequent compressed BLOB Page',
	'45bf':u'B-tree Node'
	}
	
innodb_page_direction={
	'0000': 'Unknown(0x0000)',
	'0001': 'Page Left',
	'0002': 'Page Right',
	'0003': 'Page Same Rec',
	'0004': 'Page Same Page',
	'0005': 'Page No Direction',
	'ffff': 'Unkown2(0xffff)'
}


INNODB_PAGE_SIZE=1024*16 # InnoDB Page 16K