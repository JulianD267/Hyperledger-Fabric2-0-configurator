/*
 * The Auth Token Object which includes the value and the revokation flag
 * SPDX-License-Identifier: Apache-2.0
 */

package org.example;
import org.hyperledger.fabric.contract.annotation.DataType;
import org.hyperledger.fabric.contract.annotation.Property;
import org.json.JSONObject;

@DataType()
public class DefaultAsset {

    @Property()
    private String value;

    public DefaultAsset(){        
    }
    
    public DefaultAsset(String _value){
        this.value = _value;
    }

    // ============= Getter/Setter =============
    public void setValue(final String _value) {
        this.value = _value;
    }

    /**
     * @return the value
     */
    public String getValue() {
        return value;
    }

    /**
     * This method is responsible for converting the Object to its JSON representation
     * @return         The JSON representation of the object, with all attributes
     */
    public String toJSONString() {
        return new JSONObject(this).toString();
    }

    /**
     * This method will try to extract the DefaultAsset Object out of the supplied JSON String.
     * The exact proceedings are commented.
     * @param json      The JSON formatted String that contains the object
     * @return          The Object from the JSON String
     */
    public static DefaultAsset fromJSONString(final String json) {
        String value = new JSONObject(json).getString("value");        
        DefaultAsset asset = new DefaultAsset(value);
        return asset;
    }
}
