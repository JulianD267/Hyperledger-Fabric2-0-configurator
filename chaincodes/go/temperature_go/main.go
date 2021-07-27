/*
 * SPDX-License-Identifier: Apache-2.0
 */

package main

import (
	"github.com/hyperledger/fabric-contract-api-go/contractapi"
	"github.com/hyperledger/fabric-contract-api-go/metadata"
)

func main() {
	temperatureContract := new(TemperatureContract)
	temperatureContract.Info.Version = "0.0.1"
	temperatureContract.Info.Description = "My Smart Contract"
	temperatureContract.Info.License = new(metadata.LicenseMetadata)
	temperatureContract.Info.License.Name = "Apache-2.0"
	temperatureContract.Info.Contact = new(metadata.ContactMetadata)
	temperatureContract.Info.Contact.Name = "John Doe"

	chaincode, err := contractapi.NewChaincode(temperatureContract)
	chaincode.Info.Title = "temperature_go chaincode"
	chaincode.Info.Version = "0.0.1"

	if err != nil {
		panic("Could not create chaincode from TemperatureContract." + err.Error())
	}

	err = chaincode.Start()

	if err != nil {
		panic("Failed to start chaincode. " + err.Error())
	}
}
