try { // massive try{} catch{} around the entire build for failure notifications
    timestamps {
        timeout(time: 60, unit: 'MINUTES') {
            node('fedora-28') {
                def namespace=sh(returnStdout: true, script: """python -c 'import os, json; print(json.loads(os.environ["CI_MESSAGE"])["namespace"])'""").trim()
                if(namespace != 'modules') {
                    echo "Not a change to the module namespace, skipping.."
                    echo "dist-git commit message: $CI_MESSAGE"
                    currentBuild.result = 'NOT_BUILT'
                    return
                }
                cleanWs()

                stage('Prepare ENV') {
                    sh """
                        sudo curl --insecure -o /etc/pki/ca-trust/source/anchors/RH-IT-Root-CA.pem \
                             https://password.corp.redhat.com/RH-IT-Root-CA.crt && sudo update-ca-trust extract

                        sudo curl -o /etc/yum.repos.d/rcm-tools-fedora.repo \
                             http://download.devel.redhat.com/rel-eng/RCMTOOLS/rcm-tools-fedora.repo

                        sudo dnf -y install git krb5-workstation python2 python2-pip \
                             python-gobject libmodulemd python2-pygit2

                        git clone https://github.com/yashvardhannanavati/Spade.git
                    """
                } // prepare env stage

                stage('Run Spade'){
                        sh '''#!/bin/bash
                        echo 'Hello World!'
                        '''
                } // run spade
            } // node
        } // timeout
    } // timestamps
} catch (e) {
    if (ownership.job.ownershipEnabled) {
        mail to: ownership.job.primaryOwnerEmail,
             cc: ownership.job.secondaryOwnerEmails.join(', '),
             subject: "Jenkins job ${env.JOB_NAME} #${env.BUILD_NUMBER} failed",
             body: "${env.BUILD_URL}\n\n${e}"
    }
    throw e
}
