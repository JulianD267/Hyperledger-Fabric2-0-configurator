NOCOLOR='\033[0m'
RED='\033[1;31m'
GREEN='\033[1;32m'
ORANGE='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[1;35m'
CYAN='\033[0;36m'
LIGHTGRAY='\033[0;37m'
DARKGRAY='\033[1;30m'
LIGHTRED='\033[1;31m'
LIGHTGREEN='\033[1;32m'
YELLOW='\033[1;33m'
LIGHTBLUE='\033[1;34m'
LIGHTPURPLE='\033[1;35m'
LIGHTCYAN='\033[1;36m'
WHITE='\033[1;37m'
print_test(){
  echo -e "${PURPLE}\n=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<"
  echo -e "${PURPLE}.___________. _______     _______.___________."
  echo -e "${PURPLE}|           ||   ____|   /       |           |"
  echo -e "${PURPLE}\`---|  |----\`|  |__     |   (----\`---|  |----\`"
  echo -e "${PURPLE}    |  |     |   __|     \   \       |  |     "
  echo -e "${PURPLE}    |  |     |  |____.----)   |      |  |     "
  echo -e "${PURPLE}    |__|     |_______|_______/       |__|     "
  echo -e "${PURPLE}=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<\n${NOCOLOR}"
}

help(){
  echo -e "Usage:"
  echo -e "-t <int>\t\t The Transactions per second that shall be performed (Default 1)"
  echo -e "-p <int>\t\t The amount of simultaneous processes (Default 10)"
  echo -e "-r <int>\t\t The amount of Test Runs (Default 10)"
  echo -e "-i \t\t\t Test the invoke"
  echo -e "-q \t\t\t Test the query"
  echo -e "-c [default|authtoken]\t The Chaincode which will be executed"
}

TPS=1
TEST_RUNS=10
NO_PROC=10
CONTRACT=default
PICK=i
while getopts ":t:p:r:c:ihq" option; do
   case $option in
      h)
         help
         exit;;
      r)
         TEST_RUNS=$OPTARG
         ;;
      t) # display Help
         TPS=$OPTARG
         ;;
      p)
         NO_PROC=$OPTARG
         ;;
      i)
         PICK=i
         ;;
      q)
         PICK=q
         ;;
      c)
         CONTRACT=${OPTARG}
         ;;
   esac
done

TX_PER_PROC=$(expr $TPS / $NO_PROC)


if [ $TX_PER_PROC == 0 ];
then
  exit 1
fi

test_func_invoke(){
  DELAY=$( echo "scale=5; 1.0/$1" | bc -l )
  MAX=$2
  for (( i = 0; i < $MAX; i++ )); do
    echo -e "${ORANGE}"
      ./invoke $3 $4 "[\"test${RANDOM}\"]" &
      sleep $DELAY
  done
}

test_func_query(){
  DELAY=$( echo "scale=5; 1.0/$1" | bc -l )
  MAX=$2
  for (( i = 0; i < $MAX; i++ )); do
    echo -e "${LIGHTGREEN}"
      ./query $3 $4 "[\"test${RANDOM}\"]" &
      sleep $DELAY
  done
}



if [[ $PICK = "q" ]]; then
  if [[ $CONTRACT = "default" ]]; then
    echo -e "${PURPLE}>>> Lets test the query of Default! With $TPS TPS, and $TX_PER_PROC tx per process\n${NOCOLOR}"
    for (( j = 0; j < $NO_PROC; j++ )); do
      ( test_func_query $TX_PER_PROC $TEST_RUNS fabric-default readDefaultAsset & )
    done
  elif [[ $CONTRACT = "authtoken" ]]; then
    echo -e "${PURPLE}>>> Lets test the query of AuthToken! With $TPS TPS, and $TX_PER_PROC tx per process\n${NOCOLOR}"
    for (( j = 0; j < $NO_PROC; j++ )); do
      ( test_func_query $TX_PER_PROC $TEST_RUNS fabric-authtoken readAuthToken & )
    done
  fi

elif [[ $PICK = "i" ]]; then
  if [[ $CONTRACT = "default" ]]; then
    echo -e "${PURPLE}>>> Lets test the invoke of Default! With $TPS TPS, and $TX_PER_PROC tx per process\n${NOCOLOR}"
    for (( j = 0; j < $NO_PROC; j++ )); do
      ( test_func_invoke $TX_PER_PROC $TEST_RUNS fabric-default createDefaultAsset & )
    done
  elif [[ $CONTRACT = "authtoken" ]]; then
    echo -e "${PURPLE}>>> Lets test the invoke of AuthToken! With $TPS TPS, and $TX_PER_PROC tx per process\n${NOCOLOR}"
    for (( j = 0; j < $NO_PROC; j++ )); do
      ( test_func_invoke $TX_PER_PROC $TEST_RUNS fabric-authtoken createAuthToken& )
    done
  fi

fi


exit 0
