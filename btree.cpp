/**
 * @author See Contributors.txt for code contributors and overview of BadgerDB.
 *
 * @section LICENSE
 * Copyright (c) 2012 Database Group, Computer Sciences Department, University of Wisconsin-Madison.
 */

#include "btree.h"
#include "file.h"
#include "filescan.h"
#include "exceptions/bad_index_info_exception.h"
#include "exceptions/bad_opcodes_exception.h"
#include "exceptions/bad_scanrange_exception.h"
#include "exceptions/no_such_key_found_exception.h"
#include "exceptions/scan_not_initialized_exception.h"
#include "exceptions/index_scan_completed_exception.h"
#include "exceptions/file_not_found_exception.h"
#include "exceptions/end_of_file_exception.h"
#include "exceptions/file_exists_exception.h"


//#define DEBUG

namespace badgerdb
{

// -----------------------------------------------------------------------------
// BTreeIndex::BTreeIndex -- Constructor
// -----------------------------------------------------------------------------

BTreeIndex::BTreeIndex(const std::string & relationName,
		std::string & outIndexName,
		BufMgr *bufMgrIn,
		const int attrByteOffset,
		const Datatype attrType)
{
	//constructing index name and set values
	std::ostringstream idxStr;
	idxStr << relationName << '.' << attrByteOffset;
	outIndexName = idxStr.str();
	this->bufMgr = bufMgrIn;
	this->attrByteOffset = attrByteOffset;
	this->attributeType = attrType;

	BlobFile *bFile;
	Page *metaPage, *rootPage;
	IndexMetaInfo *metainfo;

	//check if file exists. If not, create one.
	try {
		bFile = new BlobFile(outIndexName, true);


		//header page stores metadata
		bufMgr->allocPage(bFile, headerPageNum, metaPage);
		metainfo = (IndexMetaInfo *) metaPage;
		strcpy(metainfo->relationName, relationName.c_str());
		metainfo->attrByteOffset = attrByteOffset;
		metainfo->attrType = attrType;

		//root page
		bufMgr->allocPage(bFile, rootPageNum, rootPage);
		metainfo->rootPageNo = rootPageNum;
		bufMgr->unPinPage(bFile, headerPageNum, true);

		//initialize the root page
		NonLeafNodeInt *root = (NonLeafNodeInt *) rootPage;
		root->level = 0;
		int i;
		for (i = 0; i < INTARRAYNONLEAFSIZE; i++) {
			root->keyArray[i] = 0;
		}
		for(i = 0; i < INTARRAYNONLEAFSIZE + 1; i++) {
			root->pageNoArray[i] = NULL;
		}

		//leaf page
		Page *leftLeafPage, *rightLeafPage;
		PageId leftLeafNum, rightLeafNum;
		bufMgr->allocPage(bFile, leftLeafNum, leftLeafPage);
		bufMgr->allocPage(bFile, rightLeafNum, rightLeafPage);
		LeafNodeInt *leftLeaf = (LeafNodeInt *) leftLeafPage;
		LeafNodeInt *rightLeaf = (LeafNodeInt *) rightLeafPage;
		for(i = 0; i < INTARRAYLEAFSIZE; i++) {
			leftLeaf->keyArray[i] = 0;
			leftLeaf->ridArray[i] = NULL;
			rightLeaf->ridArray[i] = NULL;
			rightLeaf->keyArray[i] = 0;
		}
		leftLeaf->rightSibPageNo = rightLeafNum;
		rightLeaf->rightSibPageNo = NULL;

		root->pageNoArray[0] = leftLeafNum;
		root->pageNoArray[1] = rightLeafNum;
		bufMgr->unPinPage(bFile, leftLeafNum, true);
		bufMgr->unPinPage(bFile, rightLeafNum, true);

	} catch (FileExistsException e) {
		//file already exists, just open file
		//TODO
		bFile = new BlobFile(outIndexName, false);

		bufMgr->readPage(bFile, headerPageNum, metaPage);
		metainfo = (IndexMetaInfo *) metaPage;
		rootPageNum = metainfo->rootPageNo;
		bufMgr->unPinPage(bFile, headerPageNum, false);
	}




}


// -----------------------------------------------------------------------------
// BTreeIndex::~BTreeIndex -- destructor
// -----------------------------------------------------------------------------

BTreeIndex::~BTreeIndex()
{
}

// -----------------------------------------------------------------------------
// BTreeIndex::insertEntry
// -----------------------------------------------------------------------------

const void BTreeIndex::insertEntry(const void *key, const RecordId rid) 
{

}

// -----------------------------------------------------------------------------
// BTreeIndex::startScan
// -----------------------------------------------------------------------------

const void BTreeIndex::startScan(const void* lowValParm,
				   const Operator lowOpParm,
				   const void* highValParm,
				   const Operator highOpParm)
{

}

// -----------------------------------------------------------------------------
// BTreeIndex::scanNext
// -----------------------------------------------------------------------------

const void BTreeIndex::scanNext(RecordId& outRid) 
{

}

// -----------------------------------------------------------------------------
// BTreeIndex::endScan
// -----------------------------------------------------------------------------
//
const void BTreeIndex::endScan() 
{

}

}