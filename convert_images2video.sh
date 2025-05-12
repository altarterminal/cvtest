#!/bin/sh
set -eu

#####################################################################
# help
#####################################################################

print_usage_and_exit () {
  cat <<-USAGE 1>&2
Usage   : ${0##*/} <image dir>
Options : -o<out name> -r<frame rate> -5 -p<profile> -c<custom options>

Convert png images in <image dir> to a video.

Premise:
 - Is is assumed that each of image name is as belows.
    "prefix"_000001.png
    "prefix"_000002.png
    "prefix"_000003.png
    ...
  # "prefix" is inferred from the file numbered '*_000001.png'

-o: Specify the output video name (default: <image dir>.mp4).
-r: Specify the frame rate (default: 30).
-p: Specify the profile (default: main).
-5: Enable the encoding of H265 (default: H264).
-c: Specify the other custom options for ffmpeg (default: "").
USAGE
  exit 1
}

#####################################################################
# parameter
#####################################################################

opr=''
opt_o=''
opt_r='30'
opt_p='main'
opt_5='no'
opt_c=''

i=1
for arg in ${1+"$@"}
do
  case "${arg}" in
    -h|--help|--version) print_usage_and_exit ;;
    -o*)                 opt_o="${arg#-o}"    ;;
    -r*)                 opt_r="${arg#-r}"    ;;
    -p*)                 opt_p="${arg#-p}"    ;;
    -5)                  opt_5='yes'          ;;
    -c*)                 opt_c="${arg#-c}"    ;;
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

if ! type ffmpeg >/dev/null 2>&1; then
  echo "ERROR:${0##*/}: ffmpeg command not found" 1>&2
  exit 1
fi

if [ -z "${opr}" ]; then
  echo "ERROR:${0##*/}: image dir must be specified" 1>&2
  exit 1
elif [ ! -d "${opr}" ] || [ ! -r "${opr}" ]; then
  echo "ERROR:${0##*/}: invalid dir specified <${opr}>" 1>&2
  exit 1
else
  :
fi

if ! echo "${opt_r}" | grep -Eq '^[0-9]+$'; then
  echo "ERROR:${0##*/}: invalid frame rate specified <${opt_r}>" 1>&2
  exit 1
fi

case "${opt_p}" in
  baseline|main|high) : ;;
  *)
    echo "ERROR:${0##*/}: invalid profile specified <${opt_p}>" 1>&2
    exit 1
    ;;
esac


IMAGE_DIR="${opr}"
FRAME_RATE="${opt_r}"
PROFILE="${opt_p}"
CUSTOM_OPTIONS="${opt_c}"

if [ "${opt_5}" = 'yes' ];then
  ENCODER='libx265'
else
  ENCODER='libx264'
fi

if [ -z "${opt_o}" ]; then
  OUT_FILE="$(basename "${opr}").mp4"
else
  OUT_FILE="${opt_o%.mp4}.mp4"
fi

#####################################################################
# check video setting
#####################################################################

if ! ffmpeg -codecs 2>/dev/null | grep -q "${ENCODER}"; then
  echo "ERROR:${0##*/}: encoder not found <${ENCODER}>" 1>&2
  exit 1
fi

if [ "${ENCODER}" = 'libx265' ] && [ "${PROFILE}" != 'main' ]; then
  echo "ERROR:${0##*/}: invalid profile specified  <${PROFILE}>" 1>&2
  exit 1
fi

#####################################################################
# check prefix
#####################################################################

base_file=$(find "${IMAGE_DIR}" -name '*_000001.png' | head -n 1)

if [ -z "${base_file}" ]; then
  echo "ERROR:${0##*/}: base file named '*_000001.png' not found" 1>&2
  exit 1
fi

file_prefix="$(printf '%s\n' "${base_file}" | sed 's!_000001\.png$!!')"

#####################################################################
# main routine
#####################################################################

if ! ffmpeg                                                         \
  -y                                                                \
  -i "${file_prefix}_%06d.png"                                      \
  -pix_fmt yuv420p                                                  \
  -c:v "${ENCODER}"                                                 \
  -profile:v "${PROFILE}"                                           \
  -r "${FRAME_RATE}"                                                \
  ${CUSTOM_OPTIONS}                                                 \
  "${OUT_FILE}"; then
  echo "ERROR:${0##*/}: some error on ffmpeg" 1>&2
  exit 1
fi
