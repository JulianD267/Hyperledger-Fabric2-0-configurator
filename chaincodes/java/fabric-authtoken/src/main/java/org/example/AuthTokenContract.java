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

@Contract(name = "AuthTokenContract",
    info = @Info(title = "AuthToken contract",
                description = "Smart Contract for the im/export of authtokens",
                version = "0.0.1",
                license =
                        @License(name = "Apache-2.0",
                                url = ""),
                                contact =  @Contact(email = "julian.dreyer@hs-osnabrueck.de",
                                                name = "Julian Dreyer")))
@Default
public class AuthTokenContract implements ContractInterface {
    public  AuthTokenContract() {
    }

    /**
     * This method will check, if a token exists. Do not confuse that with the validation
     * method. This will explicitly NOT validate the Token but rather check its existence
     * @param ctx           The WorldState
     * @param authTokenId   The ID of the AuthToken to be searched
     * @return              true if it exists, false else
     */
    @Transaction()
    public boolean authTokenExists(final Context ctx, final String authTokenId) {
        byte[] buffer = ctx.getStub().getState(authTokenId);

        boolean exists = (buffer != null && buffer.length > 0);
        return exists;
    }

    /**
     * This method will check if a given token is existing and valid. To do that, it first
     * makes sure, that the token even exists. Then it will get the Token and check its
     * "isRevoked" field. If it is revoked, the token is invalid
     * @param ctx           The WorldState
     * @param authTokenId   The ID of the AuthToken to be searched
     * @return              true if it exists and is valid, false else
     */
    @Transaction()
    public boolean authTokenIsValid(final Context ctx, final String authTokenId) {
        if (authTokenExists(ctx, authTokenId)) {
            AuthToken token = AuthToken.fromJSONString(ctx.getStub().getStringState(authTokenId));
            ctx.getStub().setEvent("AuthTokenEvent", "valid".getBytes(UTF_8));
            return !token.isRevoked();
        }
        return false;
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
    public boolean createAuthToken(final Context ctx, final String value) {

        boolean exists = authTokenExists(ctx, value);
        if (exists) {
            ctx.getStub().setEvent("AuthTokenEvent", "created".getBytes(UTF_8));
            return false;
        }
        AuthToken asset = new AuthToken(value, false);
        ctx.getStub().putState(value, asset.toJSONString().getBytes(UTF_8));
        ctx.getStub().setEvent("AuthTokenEvent", "created".getBytes(UTF_8));
        return true;
    }

    /**
     * This method will read a given AuthToken from the ledger. It expects an id which will
     * then be queried. If a token is found, the Token Object will be returned.
     * @param ctx           The Worldstate
     * @param authTokenId   The ID of the desired token
     * @return              The AuthToken for the given id, or Runtime Exception
     */
    @Transaction()
    public AuthToken readAuthToken(final Context ctx, final String authTokenId) {
        boolean exists = authTokenExists(ctx, authTokenId);
        if (!exists) {
            ctx.getStub().setEvent("AuthTokenEvent", "read".getBytes(UTF_8));
            return null;
            //throw new RuntimeException("The asset " + authTokenId + " does not exist");
        }

        AuthToken newAsset = AuthToken.fromJSONString(ctx.getStub().getStringState(authTokenId));
        ctx.getStub().setEvent("AuthTokenEvent", "read".getBytes(UTF_8));
        return newAsset;
    }

    /**
     * This method will delete a given AuthToken completely. Notice that the token will be inevitably
     * removed from the ledger and NOT ONLY revoked! This method should therefore not often be used.
     * @param ctx           The WorldState
     * @param authTokenId   The ID of the desired AuthToken
     */
    @Transaction()
    public boolean deleteAuthToken(final Context ctx, final String authTokenId) {
        boolean exists = authTokenExists(ctx, authTokenId);
        if (!exists) {
            ctx.getStub().setEvent("AuthTokenEvent", "deleted".getBytes(UTF_8));
            return false;
        }
        ctx.getStub().delState(authTokenId);
        ctx.getStub().setEvent("AuthTokenEvent", "deleted".getBytes(UTF_8));
        return true;
    }

    /**
     * This method will revoke a given Token. If a valid ID is provided, the method will fetch the token,
     * set the isRevoked field to true and writes it back to the ledger.
     * @param ctx           The WorldState
     * @param authTokenId   The ID of the desired AuthToken
     * @return              true if the execution was successful.
     */
    @Transaction()
    public boolean revokeAuthToken(final Context ctx, final String authTokenId) {

        boolean exists = authTokenExists(ctx, authTokenId);
        if (!exists) {
            ctx.getStub().setEvent("AuthTokenEvent", "revoked".getBytes(UTF_8));
            return false;
        }
        AuthToken authToken = AuthToken.fromJSONString(ctx.getStub().getStringState(authTokenId));
        authToken.setRevoked(true);
        ctx.getStub().putStringState(authTokenId, authToken.toJSONString());
        ctx.getStub().setEvent("AuthTokenEvent", "revoked".getBytes(UTF_8));
        return true;
    }
}
