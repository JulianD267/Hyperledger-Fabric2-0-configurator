package gateway;

import gateway.client.CAClient;
import gateway.config.Config;
import gateway.user.UserContext;
import org.hyperledger.fabric.gateway.*;
import org.hyperledger.fabric.sdk.*;
import org.hyperledger.fabric.sdk.exception.CryptoException;
import org.hyperledger.fabric.sdk.exception.InvalidArgumentException;
import org.hyperledger.fabric.sdk.exception.ProposalException;
import org.hyperledger.fabric.sdk.exception.TransactionException;
import org.hyperledger.fabric.sdk.security.CryptoSuite;
import org.json.JSONArray;

import java.lang.reflect.InvocationTargetException;
import java.net.MalformedURLException;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.Properties;
import java.util.Random;
import java.util.concurrent.CompletableFuture;
import java.util.logging.Logger;

public class FabricService {

    private Gateway gateway;
    private Wallet wallet;
    private Channel channel;
    private HFClient hfClient;
    private Network network;

    public static void main(String[] args) {
        FabricService fabricService = new FabricService();

        try {

            // First create a new Admin user by rolling him out
            // Use the cp_certs.sh script to copy over the certificate of the CA
            Properties props = new Properties();
            props.put("pemFile", "target/classes/fabricConfig/ca.org1.dredev.de-cert.pem");
            CAClient caClient = new CAClient(Config.CA_ORG1_URL, props);
            UserContext adminUserContext = caClient.getAdminUserContext();
            if (adminUserContext == null) {
                /*
                Falls der Admin nicht existiert, wird er hier erstellt
                 */
                adminUserContext = new UserContext();
                adminUserContext.setName(Config.ADMIN);
                adminUserContext.setAffiliation(Config.ORG1);
                adminUserContext.setMspId(Config.ORG1_MSP);
                caClient.setAdminUserContext(adminUserContext);
                adminUserContext = caClient.enrollAdminUser(Config.ADMIN, Config.ADMIN_PASSWORD);
                System.out.println("The Admin is enrolled");
            }

            // Now lets properly add a wallet and Identity so we can interact with the network
            Identity identity = Identities.newX509Identity(adminUserContext.getMspId(),
                                                           adminUserContext.getEnrollment());

            fabricService.setWallet(Wallets.newFileSystemWallet(Paths.get("wallets/")));
            fabricService.getWallet().put(adminUserContext.getName(), identity);

            // Now lets establish a Gateway connection to the Fabric Network using the connection_profile.yaml
            Gateway.Builder gatewayBuilder = Gateway.createBuilder();
            fabricService.setGateway( gatewayBuilder
                        .identity(fabricService.getWallet(), adminUserContext.getName())
                        .networkConfig(Paths.get("target/classes/fabricConfig/connection_profile.yaml"))
                        .discovery(true)
                        .connect());
            // The auto discovery option will find all services for us!

            // We have to create a new HF Client now
            CryptoSuite cryptoSuite = CryptoSuite.Factory.getCryptoSuite();
            fabricService.setHfClient(HFClient.createNewInstance());
            fabricService.getHfClient().setCryptoSuite(cryptoSuite);
            fabricService.getHfClient().setUserContext(adminUserContext);
            fabricService.setNetwork(fabricService.getGateway().getNetwork("mychannel"));   // using mychannel
            fabricService.setChannel(fabricService.getNetwork().getChannel());

            // Now lets perform an invoke request to fabric-default
            TransactionProposalRequest request = fabricService.getHfClient().newTransactionProposalRequest();
            String cc = "fabric-default";                                                   // Chaincode name
            ChaincodeID ccid = ChaincodeID.newBuilder().setName(cc).build();

            request.setChaincodeID(ccid);
            request.setFcn("createDefaultAsset");                   // Chaincode invoke funktion name

            // Generate a random message to insert
            Random rand = new Random();
            int myrand = rand.nextInt();
            String[] arguments = {"Test-" + myrand}; // Arguments that Chaincode function takes
            request.setArgs(arguments);
            request.setProposalWaitTime(3000);

            // Send it off to all of the endorsement peers
            Collection<ProposalResponse> responses = fabricService.getChannel().sendTransactionProposal(request);
            System.out.println("Invoke: ");
            for (ProposalResponse res : responses) {
                // Process response from transaction proposal
                System.out.println(new String(res.getChaincodeActionResponsePayload()));
            }

            // Now send it to the orderers
            CompletableFuture<BlockEvent.TransactionEvent> cf = fabricService.getChannel().sendTransaction(responses);

            // Give it some time to broadcast the data
            Thread.sleep(1500);

            // Now lets perform a query request
            QueryByChaincodeRequest queryRequest = fabricService.getHfClient().newQueryProposalRequest();
            queryRequest.setChaincodeID(ccid);
            queryRequest.setFcn("readDefaultAsset");

            args = new String[]{"Test-" + myrand};
            queryRequest.setArgs(args);

            // We only need to send it to the peers
            Collection<ProposalResponse> queryResponses = fabricService.getChannel().queryByChaincode(queryRequest);
            System.out.println("QUERY:");
            for (ProposalResponse res : queryResponses) {
                System.out.println(new String(res.getChaincodeActionResponsePayload()));
            }

            // Finally dump all of the blockchain information as a JSON String
            BlockchainInfoDumper blockchainInfoDumper = new BlockchainInfoDumper();
            JSONArray blockchain = blockchainInfoDumper.dumpBlockchain(fabricService.getChannel(), fabricService.getHfClient());
            for(Object o: blockchain){
                System.out.println(o.toString());
            }


        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public FabricService(){

    }


    private Network getNetwork() {
        return network;
    }

    public void setGateway(Gateway gateway) {
        this.gateway = gateway;
    }

    public void setWallet(Wallet wallet) {
        this.wallet = wallet;
    }

    public void setChannel(Channel channel) {
        this.channel = channel;
    }

    public void setHfClient(HFClient hfClient) {
        this.hfClient = hfClient;
    }

    public void setNetwork(Network network) {
        this.network = network;
    }

    public Gateway getGateway() {
        return gateway;
    }

    public Wallet getWallet() {
        return wallet;
    }

    public Channel getChannel() {
        return channel;
    }

    public HFClient getHfClient() {
        return hfClient;
    }
}