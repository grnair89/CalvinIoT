
#! /bin/sh

SCRIPT_NAME=$(basename $0)

function error_desc
{

#   ---------------------------------------------------------
#       Exit the script when fatal error is encountered
#       Input argument: The error descriptor as String
#   ---------------------------------------------------------

        echo "ERROR MESSAGE DESCRIPTION!!"
        echo "${SCRIPT_NAME}: ${1:-"Unknown Error"}" 1>&2
        exit 1
}

#   ---------------------------------------------------
#         Start Calvin Runtimes on Different Nodes
#   ---------------------------------------------------

csruntime --host 10.10.10.206 --port 6000 --controlport 6001 --name runtime-0 &
if [ "$?" = "0" ]; then
        echo "Created runtime-206."
else
        error_desc "$LINENO: ERROR while starting runtime-206...ABORTING"
fi


csruntime --host 10.10.10.208 --port 6002 --controlport 6003 --name runtime-1 &
if [ "$?" = "0" ]; then
        echo "Created runtime-208."
else
        error_desc "$LINENO: ERROR while starting runtime-208...ABORTING"
fi


csruntime --host 10.10.10.209 --port 6004 --controlport 6005 --name runtime-2 &
if [ "$?" = "0" ]; then
        echo "Created runtime-209."
else
        error_desc "$LINENO: ERROR while starting runtime-209...ABORTING"
fi


csruntime --host 10.10.10.211 --port 6006 --controlport 6007 --name runtime-3 &
if [ "$?" = "0" ]; then
        echo "Created runtime-210."
else
        error_desc "$LINENO: ERROR while starting runtime-209...ABORTING"
fi


#   ---------------------------------------------------
#       Deploy two Calvin Apps on active csruntimes
#   ---------------------------------------------------
cscontrol http://localhost:6001 deploy --reqs avg_app.deployjson avgapp.calvin
if [ "$?" = "0" ]; then
        echo "Deployed avg_app.calvin"
else
        error_desc "$LINENO: ERROR during deploying avg_app.deployjson...ABORTING"
fi






# cscontrol http://localhost:6001 deploy --reqs temp_alert.deployjson temp_alert_app.calvin
# if [ "$?" = "0" ]; then
#        echo "Deployed temp_alert_app.calvin"
# else
#        error_desc "$LINENO: ERROR during deploying temp_alert_app.calvin...ABORTING"
# fi

