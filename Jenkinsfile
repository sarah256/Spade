try { // massive try{} catch{} around the entire build for failure notifications
    timestamps {
        timeout(time: 60, unit: 'MINUTES') {
            node('fedora-28') {
                cleanWs()

                stage('Prepare ENV') {
                    sh """
                        sudo curl --insecure -o /etc/pki/ca-trust/source/anchors/RH-IT-Root-CA.pem \
                             https://password.corp.redhat.com/RH-IT-Root-CA.crt && sudo update-ca-trust extract

                        sudo curl -o /etc/yum.repos.d/rcm-tools-fedora.repo \
                             http://download.devel.redhat.com/rel-eng/RCMTOOLS/rcm-tools-fedora.repo

                        sudo dnf -y install git krb5-workstation python3 python3-pip \
                             python3-gobject libmodulemd python3-pygit2 python3-yamlordereddictloader

                        git clone https://github.com/release-engineering/Spade.git
                    """
                } // prepare env stage

                stage('Run Spade'){
                    sh '''#!/bin/bash
                    if [ -n "$MESSAGE_ID" ] ; then
                        export CI_MESSAGE=$(curl "https://datagrepper.engineering.redhat.com/id?id=$MESSAGE_ID")
                    fi
                    cd Spade
                    python3 spade.py -v
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
} finally {
    def currentResult = currentBuild.result ?: 'SUCCESS'
    def script_regex = '${BUILD_LOG_REGEX, regex="^The module", maxMatches=5, showTruncatedLines=false, escapeHtml=true}'
    if (currentResult == 'SUCCESS' && manager.logContains('.* module .*')){
        emailext to: "jwboyer@redhat.com, mnewsome@redhat.com, tstellar@redhat.com, acorvin@redhat.com, rbean@redhat.com, yashn@redhat.com",
                 subject: "[factory2-spade] Module dependency overlap",
                 body: script_regex
    }
}
