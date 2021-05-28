package gateway;

import com.google.protobuf.InvalidProtocolBufferException;
import org.apache.commons.codec.binary.Hex;
import org.hyperledger.fabric.protos.ledger.rwset.kvrwset.KvRwset;
import org.hyperledger.fabric.sdk.*;
import org.hyperledger.fabric.sdk.exception.InvalidArgumentException;
import org.hyperledger.fabric.sdk.exception.ProposalException;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/*
This class is responsible for dumping the whole Blockchain. The credits mainly go to:
https://github.com/aberic/fabric-net-server/blob/master/fabric-sdk-service/src/main/java/cn/aberic/fabric/sdk/IntermediateChannel.java
 */
public class BlockchainInfoDumper {

    JSONArray dumpBlockchain(Channel channel, HFClient hfClient){
        JSONArray blockchain = new JSONArray();
        try {
            long blocks = channel.queryBlockchainInfo().getHeight();
            BlockInfo blockInfo = null;

            // Now query all the Blocks within the Blockchain for their information
            for(int blockNumber=0; blockNumber< blocks; blockNumber++){
                blockInfo = channel.queryBlockByNumber(blockNumber);
                JSONObject blockJson = new JSONObject();
                blockJson.put("blockNumber", blockNumber);
                blockJson.put("dataHash", Hex.encodeHexString(blockInfo.getDataHash()));
                blockJson.put("previousHashID", Hex.encodeHexString(blockInfo.getPreviousHash()));
                blockJson.put("calculatedBlockHash", Hex.encodeHexString(SDKUtils.calculateBlockHash(hfClient, blockNumber, blockInfo.getPreviousHash(), blockInfo.getDataHash())));
                blockJson.put("envelopeCount", blockInfo.getEnvelopeCount());
                blockJson.put("envelopes", getEnvelopeJsonArray(blockInfo, blockNumber));
                blockchain.put(blockJson);
            }

        } catch (InvalidArgumentException e) {
            e.printStackTrace();
        } catch (ProposalException e) {
            e.printStackTrace();
        } catch (InvalidProtocolBufferException e) {
            e.printStackTrace();
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return blockchain;
    }

    String parseDateFormat(Date date) {
        try {
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy/MM/dd HH:mm:ss", Locale.GERMANY);
            return sdf.format(date);
        } catch (Exception ex) {
            return "";
        }
    }

    private String printableString(final String string) {
        int maxLogStringLength = 64;
        if (string == null || string.length() == 0) {
            return string;
        }
        String ret = string.replaceAll("[^\\p{Print}]", "?");
        ret = ret.substring(0, Math.min(ret.length(), maxLogStringLength)) + (ret.length() > maxLogStringLength ? "..." : "");
        return ret;
    }

    private JSONArray getEndorserInfoJsonArray(BlockInfo.TransactionEnvelopeInfo.TransactionActionInfo txInfo, int endorsementsCount) {
        JSONArray endorserInfoJsonArray = new JSONArray();
        for (int n = 0; n < endorsementsCount; ++n) {
            BlockInfo.EndorserInfo endorserInfo = txInfo.getEndorsementInfo(n);
            String signature = Hex.encodeHexString(endorserInfo.getSignature());
            String id = endorserInfo.getId();
            String mspId = endorserInfo.getMspid();
            JSONObject endorserInfoJson = new JSONObject();

            endorserInfoJson.put("signature", signature);
            endorserInfoJson.put("id", id);
            endorserInfoJson.put("mspId", mspId);
            endorserInfoJsonArray.put(endorserInfoJson);
        }
        return endorserInfoJsonArray;
    }

    private JSONArray getArgJSONArray(int i, BlockInfo.TransactionEnvelopeInfo.TransactionActionInfo txInfo, int chaincodeInputArgsCount) throws UnsupportedEncodingException {
        JSONArray argJsonArray = new JSONArray();
        for (int z = 0; z < chaincodeInputArgsCount; ++z) {
            argJsonArray.put(printableString(new String(txInfo.getChaincodeInputArgs(z), "UTF-8")));
        }
        return argJsonArray;
    }

    private JSONArray getTransactionActionInfoJsonArray(BlockInfo.TransactionEnvelopeInfo txeInfo, int txCount) throws UnsupportedEncodingException, InvalidProtocolBufferException {
        JSONArray transactionActionInfoJsonArray = new JSONArray();
        for (int i = 0; i < txCount; i++) {
            BlockInfo.TransactionEnvelopeInfo.TransactionActionInfo txInfo = txeInfo.getTransactionActionInfo(i);
            int endorsementsCount = txInfo.getEndorsementsCount();
            int chaincodeInputArgsCount = txInfo.getChaincodeInputArgsCount();
            JSONObject transactionActionInfoJson = new JSONObject();
            transactionActionInfoJson.put("responseStatus", txInfo.getResponseStatus());
            transactionActionInfoJson.put("responseMessageString", new String(txInfo.getResponseMessageBytes(), "UTF-8"));
            transactionActionInfoJson.put("endorsementsCount", endorsementsCount);
            transactionActionInfoJson.put("chaincodeInputArgsCount", chaincodeInputArgsCount);
            transactionActionInfoJson.put("status", txInfo.getProposalResponseStatus());
            transactionActionInfoJson.put("payload", new String(txInfo.getProposalResponsePayload(), "UTF-8"));
            transactionActionInfoJson.put("chaincodeID", txInfo.getChaincodeIDName());

            transactionActionInfoJson.put("endorserInfoArray", getEndorserInfoJsonArray(txInfo, endorsementsCount));
            transactionActionInfoJson.put("argArray", getArgJSONArray(i, txInfo, chaincodeInputArgsCount));
            TxReadWriteSetInfo rwsetInfo = txInfo.getTxReadWriteSet();
            JSONObject rwsetInfoJson = new JSONObject();
            if (null != rwsetInfo) {
                int nsRWsetCount = rwsetInfo.getNsRwsetCount();
                rwsetInfoJson.put("nsRWsetCount", nsRWsetCount);
                rwsetInfoJson.put("nsRwsetInfoArray", getNsRwsetInfoJsonArray(rwsetInfo));
            }
            transactionActionInfoJson.put("rwsetInfo", rwsetInfoJson);
            transactionActionInfoJsonArray.put(transactionActionInfoJson);
        }
        return transactionActionInfoJsonArray;
    }

    private JSONArray getReadSetJSONArray(KvRwset.KVRWSet rws, String namespace) {
        JSONArray readJsonArray = new JSONArray();
        int rs = -1;
        for (KvRwset.KVRead readList : rws.getReadsList()) {
            rs++;
            String key = readList.getKey();
            long readVersionBlockNum = readList.getVersion().getBlockNum();
            long readVersionTxNum = readList.getVersion().getTxNum();
            JSONObject readInfoJson = new JSONObject();
            readInfoJson.put("namespace", namespace);
            readInfoJson.put("readSetIndex", rs);
            readInfoJson.put("key", key);
            readInfoJson.put("readVersionBlockNum", readVersionBlockNum);
            readInfoJson.put("readVersionTxNum", readVersionTxNum);
            readInfoJson.put("chaincode_version", String.format("[%s : %s]", readVersionBlockNum, readVersionTxNum));
            readJsonArray.put(readInfoJson);
        }
        return readJsonArray;
    }

    private JSONArray getWriteSetJSONArray(KvRwset.KVRWSet rws, String namespace) throws UnsupportedEncodingException {
        JSONArray writeJsonArray = new JSONArray();
        int rs = -1;
        for (KvRwset.KVWrite writeList : rws.getWritesList()) {
            rs++;
            String key = writeList.getKey();
            String valAsString = printableString(new String(writeList.getValue().toByteArray(), "UTF-8"));
            JSONObject writeInfoJson = new JSONObject();
            writeInfoJson.put("namespace", namespace);
            writeInfoJson.put("writeSetIndex", rs);
            writeInfoJson.put("key", key);
            writeInfoJson.put("value", valAsString);
            writeJsonArray.put(writeInfoJson);
        }
        return writeJsonArray;
    }

    private JSONArray getNsRwsetInfoJsonArray(TxReadWriteSetInfo rwsetInfo) throws InvalidProtocolBufferException, UnsupportedEncodingException {
        JSONArray nsRwsetInfoJsonArray = new JSONArray();
        for (TxReadWriteSetInfo.NsRwsetInfo nsRwsetInfo : rwsetInfo.getNsRwsetInfos()) {
            final String namespace = nsRwsetInfo.getNamespace();
            KvRwset.KVRWSet rws = nsRwsetInfo.getRwset();
            JSONObject nsRwsetInfoJson = new JSONObject();

            nsRwsetInfoJson.put("readSet", getReadSetJSONArray(rws, namespace));
            nsRwsetInfoJson.put("writeSet", getWriteSetJSONArray(rws, namespace));
            nsRwsetInfoJsonArray.put(nsRwsetInfoJson);
        }
        return nsRwsetInfoJsonArray;
    }

    private JSONArray getEnvelopeJsonArray(BlockInfo blockInfo, long blockNumber) throws UnsupportedEncodingException, InvalidProtocolBufferException {
        JSONArray envelopeJsonArray = new JSONArray();
        for (BlockInfo.EnvelopeInfo info : blockInfo.getEnvelopeInfos()) {
            JSONObject envelopeJson = new JSONObject();
            envelopeJson.put("channelId", info.getChannelId());
            envelopeJson.put("transactionID", info.getTransactionID());
            envelopeJson.put("validationCode", info.getValidationCode());
            envelopeJson.put("timestamp", parseDateFormat(new Date(info.getTimestamp().getTime())));
            envelopeJson.put("type", info.getType());
            envelopeJson.put("createId", info.getCreator().getId());
            envelopeJson.put("createMSPID", info.getCreator().getMspid());
            envelopeJson.put("isValid", info.isValid());
            envelopeJson.put("nonce", Hex.encodeHexString(info.getNonce()));

            if (info.getType() == BlockInfo.EnvelopeType.TRANSACTION_ENVELOPE) {
                BlockInfo.TransactionEnvelopeInfo txeInfo = (BlockInfo.TransactionEnvelopeInfo) info;
                JSONObject transactionEnvelopeInfoJson = new JSONObject();
                int txCount = txeInfo.getTransactionActionInfoCount();
                transactionEnvelopeInfoJson.put("txCount", txCount);
                transactionEnvelopeInfoJson.put("isValid", txeInfo.isValid());
                transactionEnvelopeInfoJson.put("validationCode", txeInfo.getValidationCode());
                transactionEnvelopeInfoJson.put("transactionActionInfoArray", getTransactionActionInfoJsonArray(txeInfo, txCount));
                envelopeJson.put("transactionEnvelopeInfo", transactionEnvelopeInfoJson);
            }
            envelopeJsonArray.put(envelopeJson);
        }
        return envelopeJsonArray;
    }

}
