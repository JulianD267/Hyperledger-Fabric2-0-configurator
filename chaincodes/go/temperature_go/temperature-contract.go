/*
 * SPDX-License-Identifier: Apache-2.0
 */

package main

import (
	"encoding/json"
	"fmt"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// TemperatureContract contract for managing CRUD for Temperature
type TemperatureContract struct {
	contractapi.Contract
}

// TemperatureExists returns true when asset with given ID exists in world state
func (c *TemperatureContract) TemperatureExists(ctx contractapi.TransactionContextInterface, temperatureID string) (bool, error) {
	data, err := ctx.GetStub().GetState(temperatureID)

	if err != nil {
		return false, err
	}

	return data != nil, nil
}

// CreateTemperature creates a new instance of Temperature
func (c *TemperatureContract) CreateTemperature(ctx contractapi.TransactionContextInterface, temperatureID string, value string) error {
	exists, err := c.TemperatureExists(ctx, temperatureID)
	if err != nil {
		return fmt.Errorf("Could not read from world state. %s", err)
	} else if exists {
		return fmt.Errorf("The asset %s already exists", temperatureID)
	}

	temperature := new(Temperature)
	temperature.Value = value

	bytes, _ := json.Marshal(temperature)

	return ctx.GetStub().PutState(temperatureID, bytes)
}

// ReadTemperature retrieves an instance of Temperature from the world state
func (c *TemperatureContract) ReadTemperature(ctx contractapi.TransactionContextInterface, temperatureID string) (*Temperature, error) {
	exists, err := c.TemperatureExists(ctx, temperatureID)
	if err != nil {
		return nil, fmt.Errorf("Could not read from world state. %s", err)
	} else if !exists {
		return nil, fmt.Errorf("The asset %s does not exist", temperatureID)
	}

	bytes, _ := ctx.GetStub().GetState(temperatureID)

	temperature := new(Temperature)

	err = json.Unmarshal(bytes, temperature)

	if err != nil {
		return nil, fmt.Errorf("Could not unmarshal world state data to type Temperature")
	}

	return temperature, nil
}

// UpdateTemperature retrieves an instance of Temperature from the world state and updates its value
func (c *TemperatureContract) UpdateTemperature(ctx contractapi.TransactionContextInterface, temperatureID string, newValue string) error {
	exists, err := c.TemperatureExists(ctx, temperatureID)
	if err != nil {
		return fmt.Errorf("Could not read from world state. %s", err)
	} else if !exists {
		return fmt.Errorf("The asset %s does not exist", temperatureID)
	}

	temperature := new(Temperature)
	temperature.Value = newValue

	bytes, _ := json.Marshal(temperature)

	return ctx.GetStub().PutState(temperatureID, bytes)
}

// DeleteTemperature deletes an instance of Temperature from the world state
func (c *TemperatureContract) DeleteTemperature(ctx contractapi.TransactionContextInterface, temperatureID string) error {
	exists, err := c.TemperatureExists(ctx, temperatureID)
	if err != nil {
		return fmt.Errorf("Could not read from world state. %s", err)
	} else if !exists {
		return fmt.Errorf("The asset %s does not exist", temperatureID)
	}

	return ctx.GetStub().DelState(temperatureID)
}
