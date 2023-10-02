#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
. /usr/share/beakerlib/beakerlib.sh || exit 1

rlJournalStart
	rlPhaseStartSetup
		rlRun "tmp=\$(mktemp -d)" 0 "Create tmp directory"
		rlRun "pushd $tmp"
		rlRun "set -o pipefail"
	rlPhaseEnd

	rlPhaseStartTest
		rlRun "rpm2cpio /var/share/test-artifacts/*.src.rpm | cpio -civ '*.spec'" 0 "Extract spec file from srpm"
		rlRun "cp ./*.spec $TMT_TEST_DATA/" 0 "Expose spec file"
		# The spec rpmlint is already executed from the srpm
		rlRun "rpmlint -c $TMT_PLAN_DATA/packit.toml /var/share/test-artifacts/*.rpm" 0 "Run rpmlint"
	rlPhaseEnd

	rlPhaseStartCleanup
		rlRun "popd"
		rlRun "rm -r $tmp" 0 "Remove tmp directory"
	rlPhaseEnd
rlJournalEnd
