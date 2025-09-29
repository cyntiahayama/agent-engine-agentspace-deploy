#!/bin/bash
# Deploy or update agent or no action
if [ "$DEPLOY_ACTION" == "deploy" ]; then
    python3 -c "import deploy_agent_ae; deploy_agent_ae.deploy_agent()"
elif [ "$DEPLOY_ACTION" == "update" ]; then
    python3 -c "import deploy_agent_ae.py; deploy_agent_ae.update_agent()"
fi
# Authorization action options
case $AUTH_ACTION in
    "register")
        python3 "03_register_authorization_resource.py"
        python3 "04_register_agentoauth.py"
        ;;
    "unregister")
        python3 "04b_unregister_agentoauth.py"
        python3 "03a_unregister_authorization_resource.py"
        ;;
    "reregister")
        python3 "04b_unregister_agentoauth.py"
        python3 "03a_unregister_authorization_resource.py"
        python3 "03_register_authorization_resource.py"
        python3 "04_register_agentoauth.py"
        ;;
esac