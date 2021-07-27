/*
 * SPDX-License-Identifier: Apache-2.0
 */

package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"testing"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
	"github.com/hyperledger/fabric-chaincode-go/shim"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

const getStateError = "world state get error"

type MockStub struct {
	shim.ChaincodeStubInterface
	mock.Mock
}

func (ms *MockStub) GetState(key string) ([]byte, error) {
	args := ms.Called(key)

	return args.Get(0).([]byte), args.Error(1)
}

func (ms *MockStub) PutState(key string, value []byte) error {
	args := ms.Called(key, value)

	return args.Error(0)
}

func (ms *MockStub) DelState(key string) error {
	args := ms.Called(key)

	return args.Error(0)
}

type MockContext struct {
	contractapi.TransactionContextInterface
	mock.Mock
}

func (mc *MockContext) GetStub() shim.ChaincodeStubInterface {
	args := mc.Called()

	return args.Get(0).(*MockStub)
}

func configureStub() (*MockContext, *MockStub) {
	var nilBytes []byte

	testTemperature := new(Temperature)
	testTemperature.Value = "set value"
	temperatureBytes, _ := json.Marshal(testTemperature)

	ms := new(MockStub)
	ms.On("GetState", "statebad").Return(nilBytes, errors.New(getStateError))
	ms.On("GetState", "missingkey").Return(nilBytes, nil)
	ms.On("GetState", "existingkey").Return([]byte("some value"), nil)
	ms.On("GetState", "temperaturekey").Return(temperatureBytes, nil)
	ms.On("PutState", mock.AnythingOfType("string"), mock.AnythingOfType("[]uint8")).Return(nil)
	ms.On("DelState", mock.AnythingOfType("string")).Return(nil)

	mc := new(MockContext)
	mc.On("GetStub").Return(ms)

	return mc, ms
}

func TestTemperatureExists(t *testing.T) {
	var exists bool
	var err error

	ctx, _ := configureStub()
	c := new(TemperatureContract)

	exists, err = c.TemperatureExists(ctx, "statebad")
	assert.EqualError(t, err, getStateError)
	assert.False(t, exists, "should return false on error")

	exists, err = c.TemperatureExists(ctx, "missingkey")
	assert.Nil(t, err, "should not return error when can read from world state but no value for key")
	assert.False(t, exists, "should return false when no value for key in world state")

	exists, err = c.TemperatureExists(ctx, "existingkey")
	assert.Nil(t, err, "should not return error when can read from world state and value exists for key")
	assert.True(t, exists, "should return true when value for key in world state")
}

func TestCreateTemperature(t *testing.T) {
	var err error

	ctx, stub := configureStub()
	c := new(TemperatureContract)

	err = c.CreateTemperature(ctx, "statebad", "some value")
	assert.EqualError(t, err, fmt.Sprintf("Could not read from world state. %s", getStateError), "should error when exists errors")

	err = c.CreateTemperature(ctx, "existingkey", "some value")
	assert.EqualError(t, err, "The asset existingkey already exists", "should error when exists returns true")

	err = c.CreateTemperature(ctx, "missingkey", "some value")
	stub.AssertCalled(t, "PutState", "missingkey", []byte("{\"value\":\"some value\"}"))
}

func TestReadTemperature(t *testing.T) {
	var temperature *Temperature
	var err error

	ctx, _ := configureStub()
	c := new(TemperatureContract)

	temperature, err = c.ReadTemperature(ctx, "statebad")
	assert.EqualError(t, err, fmt.Sprintf("Could not read from world state. %s", getStateError), "should error when exists errors when reading")
	assert.Nil(t, temperature, "should not return Temperature when exists errors when reading")

	temperature, err = c.ReadTemperature(ctx, "missingkey")
	assert.EqualError(t, err, "The asset missingkey does not exist", "should error when exists returns true when reading")
	assert.Nil(t, temperature, "should not return Temperature when key does not exist in world state when reading")

	temperature, err = c.ReadTemperature(ctx, "existingkey")
	assert.EqualError(t, err, "Could not unmarshal world state data to type Temperature", "should error when data in key is not Temperature")
	assert.Nil(t, temperature, "should not return Temperature when data in key is not of type Temperature")

	temperature, err = c.ReadTemperature(ctx, "temperaturekey")
	expectedTemperature := new(Temperature)
	expectedTemperature.Value = "set value"
	assert.Nil(t, err, "should not return error when Temperature exists in world state when reading")
	assert.Equal(t, expectedTemperature, temperature, "should return deserialized Temperature from world state")
}

func TestUpdateTemperature(t *testing.T) {
	var err error

	ctx, stub := configureStub()
	c := new(TemperatureContract)

	err = c.UpdateTemperature(ctx, "statebad", "new value")
	assert.EqualError(t, err, fmt.Sprintf("Could not read from world state. %s", getStateError), "should error when exists errors when updating")

	err = c.UpdateTemperature(ctx, "missingkey", "new value")
	assert.EqualError(t, err, "The asset missingkey does not exist", "should error when exists returns true when updating")

	err = c.UpdateTemperature(ctx, "temperaturekey", "new value")
	expectedTemperature := new(Temperature)
	expectedTemperature.Value = "new value"
	expectedTemperatureBytes, _ := json.Marshal(expectedTemperature)
	assert.Nil(t, err, "should not return error when Temperature exists in world state when updating")
	stub.AssertCalled(t, "PutState", "temperaturekey", expectedTemperatureBytes)
}

func TestDeleteTemperature(t *testing.T) {
	var err error

	ctx, stub := configureStub()
	c := new(TemperatureContract)

	err = c.DeleteTemperature(ctx, "statebad")
	assert.EqualError(t, err, fmt.Sprintf("Could not read from world state. %s", getStateError), "should error when exists errors")

	err = c.DeleteTemperature(ctx, "missingkey")
	assert.EqualError(t, err, "The asset missingkey does not exist", "should error when exists returns true when deleting")

	err = c.DeleteTemperature(ctx, "temperaturekey")
	assert.Nil(t, err, "should not return error when Temperature exists in world state when deleting")
	stub.AssertCalled(t, "DelState", "temperaturekey")
}
