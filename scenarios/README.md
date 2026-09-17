# Incident Scenarios

This directory contains deterministic, reproducible incident scenarios for evaluating the RCA agent.
Each scenario consists of a trigger, validation, and reset script.

## Structure
- `oom/`: A workload that intentionally consumes memory until it is OOMKilled.
- `bad-deployment/`: An intentional deployment of an invalid image tag resulting in ImagePullBackOff.
- `dependency-failure/`: The `payment` service is deleted, causing cascading 502 Bad Gateway errors upstream to `checkout` and `frontend`.

## Usage
Use the `run.sh` script to manage scenarios:

```bash
# Trigger an incident
./scenarios/run.sh trigger oom
./scenarios/run.sh trigger bad-deployment
./scenarios/run.sh trigger dependency-failure

# Validate the incident evidence
./scenarios/run.sh validate oom
./scenarios/run.sh validate bad-deployment
./scenarios/run.sh validate dependency-failure

# Reset the cluster to a healthy state
./scenarios/run.sh reset oom
./scenarios/run.sh reset bad-deployment
./scenarios/run.sh reset dependency-failure
```

*Note: Each scenario folder contains a hidden `ground_truth.json` file used strictly for validation. The RCA agent should never access these files during its investigation.*
