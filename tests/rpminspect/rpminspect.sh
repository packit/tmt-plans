#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
. /usr/share/beakerlib/beakerlib.sh || exit 1

rlJournalStart
	rlPhaseStartSetup
		# TODO: Add interface to get necessary rpminspect.yaml
		# fetch-my-conf.py
		rlRun "freshclam" 0 "Update clam antivirus database"
		rlRun "tmp=\$(mktemp -d)" 0 "Create tmp directory"
		rlRun "pushd $tmp"
		rlRun "set -o pipefail"
		rlRun "mkdir -p ./inspect_builds/$PACKIT_PACKAGE_NVR" 0 "Make basic directory layout"
	rlPhaseEnd

	rlPhaseStartTest
		# Get OS info of the current distro. Maybe there is a more modern approach?
		source /etc/os-release
		# Get the most recent koji build
		if [[ -n "${RPMINSPECT_KOJI_BUILD}" ]]; then
				rlFail "Not implemented for koji tags"
		else
			if rlIsFedora || rlIsCentOS; then
				# TODO: Allow for other variables defining PACKAGE_NAME
				rlIsFedora && rlRun "tag=f${VERSION_ID}" 0 "Set Fedora tag"
				rlIsCentOS && rlRun "tag=epel${VERSION_ID}" 0 "Set Epel tag"
				rlRun -s "/usr/bin/koji list-tagged --latest --inherit --quiet ${tag} ${PACKIT_PACKAGE_NAME}" 0 "Get latest koji build"
				rlRun "latest_build=\$(cat $rlRun_LOG | sed 's/\s.*//')" 0 "Resolve latest_build variable"
				if [[ -n "$latest_build" ]]; then
					## If the package is already uploaded downstream
					rlRun "args=\"-v -c ${RPMINSPECT_CONFIG:-/usr/share/rpminspect/${ID}.yaml}\"" 0 "Set args: Default and required options"
					rlRun "args=\"\$args -f  -w ./inspect_builds\"" 0 "Set args: Fetch and write to ./inspect_builds"
					# TODO: Should have a better way to get the current arch to cover emulated and other cases
					rlRun "args=\"\$args --arches=src,noarch,$(arch)\"" 0 "Set args: Specify the architectures"
					rlRun "args=\"\$args \$latest_build\" && echo \$args" 0 "Set args: latest_build"
					rlRun "/usr/bin/rpminspect $args" 0 "Downloading latest koji builds"
				fi
			else
				rlFail "Not implemented for tags other than fedora or centos"
			fi
		fi
		# Copy current artifact builds to koji-like file structure
		for type in src noarch "$(arch)"; do
			if [[ -n "$(find /var/share/test-artifacts -name "*.${type}.rpm" -print -quit)" ]]; then
				rlRun "mkdir ./inspect_builds/$PACKIT_PACKAGE_NVR/$type" 0 "Create necessary file structure"
				rlRun "cp /var/share/test-artifacts/*.$type.rpm ./inspect_builds/$PACKIT_PACKAGE_NVR/$type/" 0 "Copy all rpms from testing-farm"
			fi
		done
		rlRun "tree ./inspect_builds"

		## Do actual rpminspect
		rlRun "args=\"-v -c ${RPMINSPECT_CONFIG:-/usr/share/rpminspect/${ID}.yaml}\"" 0 "Set args: Default and required options"
		rlRun "args=\"\$args --output=$TMT_TEST_DATA/result.json --format=json\"" 0 "Set args: Output the data to json"
		# Specify the test to run
		if [[ -n "$RPMINSPECT_TESTS" ]]; then
			# Takes precedence over --exclude
			rlRun "args=\"\$args --tests=$RPMINSPECT_TESTS\"" 0 "Set args: Run only specified tests"
		elif [[ -n "$RPMINSPECT_EXCLUDE" ]]; then
			# Only run if there is no RPMINSPECT_TESTS
			rlRun "args=\"\$args --exclude=${RPMINSPECT_EXCLUDE}\"" 0 "Set args: Exclude test lists given"
		else
			# TODO: Only exclude metadata if running with copr
			# https://tmt.readthedocs.io/en/stable/spec/context.html#initiator
			rlRun "args=\"\$args --exclude=metadata\"" 0 "Set args: Exclude metadata on copr"
		fi
		[[ -n "$RPMINPSECT_ARCHES" ]] && rlRun "args=\"\$args --arches=$RPMINPSECT_ARCHES\"" 0 "Set args: Run rpminspect for the specified architectures"
		[[ -n "$latest_build" ]] && rlRun "args=\"\$args ./inspect_builds/$latest_build\"" 0 "Set args: Use latest_build as before_build"
		rlRun "args=\"\$args --threshold=${RPMINSPECT_THRESHOLD:-BAD}\"" 0 "Set args: Failure threshold"
		[[ -n "${RPMINSPECT_SUPPRESS}" ]] && rlRun "args=\"\$args --suppress=${RPMINSPECT_SUPPRESS}\"" 0 "Set args: Suppress threshold"
		rlRun "args=\"\$args ./inspect_builds/$PACKIT_PACKAGE_NVR\" && echo \$args" 0 "Set args: Set downloaded source as after_build"
	  rlRun "/usr/bin/rpminspect $args" 0 "Run rpminspect"
	  # Calculate results only if result.json was produced
	  if [[ -f "$TMT_TEST_DATA/result.json" ]]; then
			# Get the number of BAD and VERIFY check results
			# Note about jq syntax used:
			# - .[][]               : collapse the dict of list of objects into a series of objects
			# - select(.result ...) : filter the series of objects by the `result` value
			# - [ ... ] | length    : create a list of the filtered object series and count the length
			rlRun "bad_results=\$(jq '[.[][] | select(.result == \"BAD\")] | length' $TMT_TEST_DATA/result.json)" 0 "Count the BAD check results"
			rlRun "verify_results=\$(jq '[.[][] | select(.result == \"VERIFY\")] | length' $TMT_TEST_DATA/result.json)" 0 "Count the VERIFY check results"
			rlRun "info_results=\$(jq '[.[][] | select(.result == \"INFO\")] | length' $TMT_TEST_DATA/result.json)" 0 "Count the INFO check results"
			rlRun "ok_results=\$(jq '[.[][] | select(.result == \"OK\")] | length' $TMT_TEST_DATA/result.json)" 0 "Count the OK check results"
			rlRun "cp $TMT_PLAN_DATA/viewer.html $TMT_TEST_DATA/viewer.html"
		fi
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
	# Otherwise take the highest result status of the rpminspect checks
	# BAD > VERIFY > INFO > OK
	if (( bad_results > 0 )); then
		result=fail
	elif (( verify_results > 0 )); then
		# TODO: Switch result to warn when testing-farm supports it
		result=info
	elif (( info_results > 0 )); then
		result=info
	else
		result=pass
	fi
fi
# Write the actual results.yaml
if [[ -f "$TMT_TEST_DATA/results.json" ]]; then
	# Add rpminspect results
	cat <<-EOF >> "$TMT_TEST_DATA/results.yaml"
	- name: /
		result: ${result}
		note: ${bad_results} BAD, ${verify_results} VERIFY, ${info_results} INFO, ${ok_results} OK
		log:
			- ../output.txt
			- ../journal.txt
			- ../journal.xml
			- viewer.html
			- result.json
	EOF
else
	# Add the beakerlib data only
	cat <<-EOF >> "$TMT_TEST_DATA/results.yaml"
	- name: /
		result: ${result}
		log:
			- ../output.txt
			- ../journal.txt
			- ../journal.xml
	EOF
fi
