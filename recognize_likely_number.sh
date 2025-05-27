#!/bin/sh
set -eu

#####################################################################
# help
#####################################################################

print_usage_and_exit () {
  cat <<-USAGE 1>&2
Usage   : ${0##*/} <file pattern>
Options : 

Recognize a most likey number from images.
Pathname expansion can be used for <file pattern>.
USAGE
  exit 1
}

#####################################################################
# parameter
#####################################################################

opr=''

i=1
for arg in ${1+"$@"}
do
  case "${arg}" in
    -h|--help|--version) print_usage_and_exit ;;
    *)
      if [ $i -eq $# ] && [ -z "${opr}" ]; then
        opr="${arg}"
      else
        echo "ERROR:${0##*/}: invalid args" 1>&2
        exit 1
      fi
      ;;
  esac

  i=$((i + 1))
done

if ! type ocrad >/dev/null 2>&1; then
  echo "ERROR:${0##*/}: ocrad command not found" 1>&2
  exit 1
fi

FILE_PATTERN="${opr}"

#####################################################################
# main routine
#####################################################################

find . -name "${FILE_PATTERN}"                                      |

while read -r image_file
do
  ocrad -i --filter=numbers_only "${image_file}"                    |
  grep -v '^$'
done                                                                |

while read -r result
do
  if echo "${result}" | grep -Eq '^[0-9]+$'; then
    echo "${result}"
  fi
done                                                                |

awk '
{ print; }
END {
  if (NR == 0) {
    printf "WARN:'"${0##*/}"': there is no result <'"${FILE_PATTERN}"'>"
  }
}
'                                                                   |

sort                                                                |
tail -n 1
