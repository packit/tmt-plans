#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
. /usr/share/beakerlib/beakerlib.sh || exit 1

rlJournalStart
	rlPhaseStartSetup
		rlRun "tmp=\$(mktemp -d)" 0 "Create tmp directory"
		rlRun "work_dir=$(pwd)" 0 "Save original work_dir"
		rlRun "pushd $tmp"
		rlRun "set -o pipefail"
		rlIsCentOS && rlLogWarning "rpmlint on CentOS+Epel is outdated. Reported information might not be relevant"
	rlPhaseEnd

	rlPhaseStartTest
		if [[ -f "$TMT_PLAN_DATA/rpmlint.toml" ]]; then
			# A custom rpmlint toml file was provided. Use that instead of the local files
			rlRun "config_file=$TMT_PLAN_DATA/rpmlint.toml" 0 "Use config file from plan data"
		else
			# TODO: Use packit.toml only in packit context
			rlRun "config_file=$work_dir/tests/rpmlint/packit.toml" 0 "Use the provided packit config file"
		fi
		rlRun "rpm2cpio /var/share/test-artifacts/*.src.rpm | cpio -civ '*.spec'" 0 "Extract spec file from srpm"
		rlRun "cp ./*.spec $TMT_TEST_DATA/" 0 "Expose spec file"
		# Dummy loop over spec file to extract the file name
		for spec_file in *.spec; do
			# Extract the base name from the file name and save it in BASH_REMATCH
			[[ $spec_file =~ (.*).spec ]];
			# Only use rpmlintrc file with the same name as the spec file
			[[ -f "$TMT_PLAN_DATA/${BASH_REMATCH[1]}.rpmlintrc" ]] && rlRun "rc_file=$TMT_PLAN_DATA/${BASH_REMATCH[1]}.rpmlintrc" 0 "Use the rpmlintrc file of $spec_file"
		done
		# The spec rpmlint is already executed from the srpm
		rlIsCentOS || rlRun "rpmlint -c $config_file ${rc_file:+"-r $rc_file"} /var/share/test-artifacts/*.rpm" 0 "Run rpmlint (non-CentOS)"
		rlIsCentOS && rlRun "rpmlint /var/share/test-artifacts/*.rpm || true" 0 "Run rpmlint (CentOS)"
	rlPhaseEnd

	rlPhaseStartCleanup
		rlRun "popd"
		rlRun "rm -r $tmp" 0 "Remove tmp directory"
	rlPhaseEnd
rlJournalEnd
