/*
 * The Auth Token Object which includes the value and the revokation flag
 * SPDX-License-Identifier: Apache-2.0
 */

package org.example;

import java.io.UnsupportedEncodingException;
import java.nio.charset.Charset;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Date;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import org.hyperledger.fabric.contract.annotation.DataType;
import org.hyperledger.fabric.contract.annotation.Property;
import org.json.JSONObject;

@DataType()
public class AuthToken {

    // ============= Attributes =============
    private String saltString;

    @Property()
    private String value;

    @Property()
    private boolean revoked;

    public AuthToken(){
        // Generate a unique salt
        DateFormat dateFormat = new SimpleDateFormat("yyyyMMddHH");
	      Date date = new Date();
        saltString = new String(dateFormat.format(date));
    }

    public AuthToken(final String _value, final boolean _revoked){
        this.revoked = _revoked;
        this.value = _value;
        // Generate a unique salt
        DateFormat dateFormat = new SimpleDateFormat("yyyyMMddHH");
	      Date date = new Date();
        saltString = new String(dateFormat.format(date));
    }

    // ============= Getter/Setter =============
    public boolean isRevoked(){
        return this.revoked;
    }

    public void setRevoked(final boolean _revoked){
        this.revoked = _revoked;
    }
    public String getValue() {
        return value;
    }

    public void setValue(final String _value) {
        this.value = hashString(_value);
    }

    public String getSaltString() {
        return saltString;
    }

    public void setSaltString(final String _saltString) {
        this.saltString = _saltString;
    }

    // ============= Methods =============
     /**
     * This method is responsible for hashing the password. The stored passwords are not
     * to be stored in Plaintext within the Blockchain!!! Thus this method will apply the
     * SHA-256 Algorithm in combination with a random Salt.
     * @param data      The data that will be hashed and salted
     * @return          The hashed data+salt
     */
    private String hashString(final String data) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            //Salt the Hash
            byte[] encodedHash = digest.digest((data + saltString).getBytes("UTF-8"));
            StringBuffer buffer = new StringBuffer();
            for (int i = 0; i < encodedHash.length; i++) {
                final int magicNo = 0xff;
                String hex = Integer.toHexString(magicNo & encodedHash[i]);
                if (hex.length() == 1) {
                    buffer.append('0');
                }
                buffer.append(hex);
            }
            String pw = buffer.toString();
            return pw;
        } catch(NoSuchAlgorithmException e) {
            e.printStackTrace();
        } catch(UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        return "";
    }

    /**
     * This method is responsible for converting the Object to its JSON representation
     * @return         The JSON representation of the object, with all attributes
     */
    public String toJSONString() {
        return new JSONObject(this).toString();
    }

    /**
     * This method will try to extract the AuthToken Object out of the supplied JSON String.
     * The exact proceedings are commented.
     * @param json      The JSON formatted String that contains the object
     * @return          The Object from the JSON String
     */
    public static AuthToken fromJSONString(final String json) {
        JSONObject authToken = new JSONObject(json);
        String value = authToken.getString("value");
        String salt = authToken.getString("saltString");
        boolean revoked = authToken.getBoolean("revoked");

        AuthToken asset = new AuthToken();
        asset.setSaltString(salt);
        asset.setValue(value);
        asset.setRevoked(revoked);
        return asset;
    }
}
