// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CheckpointContract {
    struct Checkpoint {
        string direccion;
        string estado;
        string hashDato;
        uint256 timestamp;
    }

    mapping(uint => Checkpoint) public checkpoints;
    uint public totalCheckpoints;

    event CheckpointCreado(uint id, string direccion, string estado, string hashDato, uint timestamp);

    function agregarCheckpoint(string memory _direccion, string memory _estado, string memory _hashDato) public {
        totalCheckpoints++;
        checkpoints[totalCheckpoints] = Checkpoint(_direccion, _estado, _hashDato, block.timestamp);
        emit CheckpointCreado(totalCheckpoints, _direccion, _estado, _hashDato, block.timestamp);
    }

    function obtenerCheckpoint(uint _id) public view returns (string memory, string memory, string memory, uint256) {
        Checkpoint memory c = checkpoints[_id];
        return (c.direccion, c.estado, c.hashDato, c.timestamp);
    }
}
