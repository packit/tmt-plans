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
					# If the package is already uploaded downstream
					# TODO: Should have a better way to get the current arch to cover emulated and other cases
					rlRun "/usr/bin/rpminspect -v -c ${RPMINSPECT_CONFIG:-/usr/share/rpminspect/fedora.yaml} -f -w ./inspect_builds --arches=src,noarch,$(arch) $latest_build" 0 "Downloading latest koji builds"
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

		# Do actual rpminspect
		args=""
		args="$args -c ${RPMINSPECT_CONFIG:-/usr/share/rpminspect/fedora.yaml}"
		args="$args --output=${TMT_TEST_DATA}/result.json --format=json"
		args="$args --verbose"
		# TODO: Only exclude if running with copr
		args="$args --exclude=metadata"
		args="$args ${ARCHES:+--arches=$ARCHES}"
		args="$args ${RPMINSPECT_TESTS:+--tests=$RPMINSPECT}"
		if [[ -n "$latest_build" ]]; then
			args="$args ./inspect_builds/$latest_build"
		fi
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
