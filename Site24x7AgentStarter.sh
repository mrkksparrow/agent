#!/bin/bash

DOWN_MSG="Site24x7 monitoring agent service is down"

AGENT_STATUS_OP=$(/opt/site24x7/monagent/bin/monagent status)

if [ "$AGENT_STATUS_OP" = "$DOWN_MSG" ]; then
	/opt/site24x7/monagent/bin/monagent restart
fi
