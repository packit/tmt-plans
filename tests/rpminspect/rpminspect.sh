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
			if rlIsFedora; then
				# TODO: Allow for other variables defining PACKAGE_NAME
				rlRun -s "/usr/bin/koji list-tagged --latest --inherit --quiet f${VERSION_ID} ${PACKIT_PACKAGE_NAME}" 0 "Get latest koji build"
				rlRun "latest_build=\$(cat $rlRun_LOG | sed 's/\s.*//')" 0 "Resolve latest_build variable"
				if [[ -n "$latest_build" ]]; then
					## If the package is already uploaded downstream
					# Default and required options
					args="-v -c ${RPMINSPECT_CONFIG:-/usr/share/rpminspect/fedora.yaml}"
					# Fetch and write to ./inspect_builds
					args="$args -f  -w ./inspect_builds"
					# Specify the architectures
					# TODO: Should have a better way to get the current arch to cover emulated and other cases
					args="$args --arches=src,noarch,$(arch)"
     					args="$args $latest_build"
					rlRun "/usr/bin/rpminspect $args" 0 "Downloading latest koji builds"
				fi
			else
				rlFail "Not implemented for tags other than fedora"
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
		# Default and required options
		args="-v -c ${RPMINSPECT_CONFIG:-/usr/share/rpminspect/fedora.yaml}"
		# Output the data to json so that it can be displayed
		args="$args --output=$TMT_TEST_DATA/result.json --format=json"
		# Specify the test to run
		if [[ -n "$RPMINSPECT_TESTS" ]]; then
			# Run only specified tests. Takes precedence over --exclude
			args="$args --tests=$RPMINSPECT_TESTS"
		elif [[ -n "$RPMINSPECT_EXCLUDE" ]]; then
			# Exclude test lists given. Only run if there is no RPMINSPECT_TESTS
		 	args="$args --exclude=${RPMINSPECT_EXCLUDE:-metadata}"
		else
			# TODO: Only exclude metadata if running with copr
			# https://tmt.readthedocs.io/en/stable/spec/context.html#initiator
			args="$args --exclude=metadata"
		fi
		# Run rpminspect for the specified architectures
		[[ -n "$RPMINPSECT_ARCHES" ]] && args="$args --arches=$RPMINPSECT_ARCHES"
		# If we have a previous build to compare with, use that as before_build
		[[ -n "$latest_build" ]] && args="$args ./inspect_builds/$latest_build"
		# The remaining part is treated as the after_build/the build to be inspected
		args="$args ./inspect_builds/$PACKIT_PACKAGE_NVR"
	  rlRun "/usr/bin/rpminspect $args" 0 "Run rpminspect"
		rlRun "cp $TMT_PLAN_DATA/viewer.html $TMT_TEST_DATA/viewer.html"
	rlPhaseEnd

	rlPhaseStartCleanup
		rlRun "popd"
		rlRun "rm -r $tmp" 0 "Remove tmp directory"
		# Note: $TESTRESULT_RESULT_STRING is not made available. Using $__INTERNAL_PHASES_WORST_RESULT instead
		cat <<EOF > "$TMT_TEST_DATA/results.yaml"
- name: /rpminspect
  result: ${__INTERNAL_PHASES_WORST_RESULT,,}
  log:
    - ../output.txt
    - ../journal.txt
    - ../journal.xml
    - viewer.html
    - result.json
EOF
	rlPhaseEnd
rlJournalEnd
