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
		rlIsCentOS || rlRun -s "rpmlint -c $config_file ${rc_file:+"-r $rc_file"} /var/share/test-artifacts/*.rpm" 0 "Run rpmlint (non-CentOS)"
		rlIsCentOS && rlRun -s "rpmlint /var/share/test-artifacts/*.rpm || true" 0 "Run rpmlint (CentOS)"
		# Read the output and extract the error/warning messages
		re_pattern="([0-9]+) packages and ([0-9]+) specfiles checked; ([0-9]+) errors, ([0-9]+) warnings(, ([0-9]+) filtered, ([0-9]+) badness)?"
		while IFS= read -r line; do
			if [[ $line =~ $re_pattern ]]; then
				rlRun "error_count=${BASH_REMATCH[3]}" 0 "Saving error_count"
				rlRun "warning_count=${BASH_REMATCH[4]}" 0 "Saving warning_count"
				rlRun "filtered_count=${BASH_REMATCH[6]:-?}" 0 "Saving filtered_count"
				rlRun "badness_count=${BASH_REMATCH[7]:-?}" 0 "Saving badness_count"
				break
			fi
		done < "$rlRun_LOG"
	rlPhaseEnd

	rlPhaseStartCleanup
		rlRun "popd"
		rlRun "rm -r $tmp" 0 "Remove tmp directory"
	rlPhaseEnd
rlJournalEnd

# Report the test results
source $BEAKERLIB_DIR/TestResults
if [[ ${TESTRESULT_RESULT_STRING,,} != pass ]]; then
	# If test failed or triggerred warning within the test itself, use that outcome
	result=${TESTRESULT_RESULT_STRING,,}
else
	# Otherwise take the highest result status of the rpmlint results
	if (( error_count > 0 )); then
		result=fail
	elif (( warning_count > 0 )); then
		result=warn
	elif (( badness_count > 0 )); then
		result=info
	else
		result=pass
	fi
fi
# Write the actual results.yaml
cat <<EOF >> "$TMT_TEST_DATA/results.yaml"
- name: /
  result: ${result}
  note: ${error_count} errors, ${warning_count} warnings, ${filtered_count} filtered, ${badness_count} badness
  log:
    - ../output.txt
    - ../journal.txt
    - ../journal.xml
EOF
