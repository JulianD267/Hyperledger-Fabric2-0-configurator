/*
 * SPDX-License-Identifier: Apache-2.0
 */
package org.example;

import org.hyperledger.fabric.contract.Context;
import org.hyperledger.fabric.contract.ContractInterface;
import org.hyperledger.fabric.contract.annotation.Contract;
import org.hyperledger.fabric.contract.annotation.Default;
import org.hyperledger.fabric.contract.annotation.Transaction;
import org.hyperledger.fabric.contract.annotation.Contact;
import org.hyperledger.fabric.contract.annotation.Info;
import org.hyperledger.fabric.contract.annotation.License;
import static java.nio.charset.StandardCharsets.UTF_8;

@Contract(name = "DefaultContract",
    info = @Info(title = "Default Contract",
                description = "Smart Contract for the im/export of default objects",
                version = "0.0.1",
                license =
                        @License(name = "Apache-2.0",
                                url = ""),
                                contact =  @Contact(email = "julian.dreyer@hs-osnabrueck.de",
                                                name = "Julian Dreyer")))
@Default
public class DefaultContract implements ContractInterface {
    public  DefaultContract() {
    }

    /**
     * This method will check, if a DefaultAsset exists. Do not confuse that with the validation
     * method. This will explicitly NOT validate the Token but rather check its existence
     * @param ctx           The WorldState
     * @param authTokenId   The ID of the AuthToken to be searched
     * @return              true if it exists, false else
     */
    @Transaction()
    public boolean defaultAssetExists(final Context ctx, final String _id) {
        byte[] buffer = ctx.getStub().getState(_id);

        boolean exists = (buffer != null && buffer.length > 0);
        return exists;
    }

  
    /**
     * This method will create a new AuthToken and write it to the ledger. For that it needs the
     * value, so the token itself. It will then check if the Token already exists. If not, a new
     * AuthToken object will be created. Its fields will be set accordingly.
     * @param ctx       The WorldState
     * @param value     The token value
     * @return          true, if the execution was successful, false else
     */
    @Transaction()
    public boolean createDefaultAsset(final Context ctx, final String value) {

        boolean exists = defaultAssetExists(ctx, value);
        if (exists) {
            ctx.getStub().setEvent("DefaultEvent", "created".getBytes(UTF_8));
            return false;
        }
        DefaultAsset asset = new DefaultAsset(value);
        ctx.getStub().putState(value, asset.toJSONString().getBytes(UTF_8));
        ctx.getStub().setEvent("DefaultEvent", "created".getBytes(UTF_8));
        return true;
    }

    /**
     * This method will read a given DefaultAsset from the ledger. It expects an id which will
     * then be queried. If a token is found, the Token Object will be returned.
     * @param ctx           The Worldstate
     * @param _id   The ID of the desired token
     * @return              The AuthToken for the given id, or Runtime Exception
     */
    @Transaction()
    public DefaultAsset readDefaultAsset(final Context ctx, final String _id) {
        boolean exists = defaultAssetExists(ctx, _id);
        if (!exists) {
            ctx.getStub().setEvent("DefaultEvent", "read".getBytes(UTF_8));
            return null;
            //throw new RuntimeException("The asset " + _id + " does not exist");
        }

        DefaultAsset newAsset = DefaultAsset.fromJSONString(ctx.getStub().getStringState(_id));
        ctx.getStub().setEvent("DefaultEvent", "read".getBytes(UTF_8));
        return newAsset;
    }

    /**
     * This method will delete a given AuthToken completely. Notice that the token will be inevitably
     * removed from the ledger and NOT ONLY revoked! This method should therefore not often be used.
     * @param ctx           The WorldState
     * @param _id   The ID of the desired AuthToken
     */
    @Transaction()
    public boolean deleteDefaultAsset(final Context ctx, final String _id) {
        boolean exists = defaultAssetExists(ctx, _id);
        if (!exists) {
            ctx.getStub().setEvent("DefaultEvent", "deleted".getBytes(UTF_8));
            return false;
        }
        ctx.getStub().delState(_id);
        ctx.getStub().setEvent("DefaultEvent", "deleted".getBytes(UTF_8));
        return true;
    }
}
