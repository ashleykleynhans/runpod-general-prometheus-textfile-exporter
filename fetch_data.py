#!/usr/bin/env python3
import json
import os
import sys
import httpx
import yaml


def load_config(script_path):
    try:
        config_file = f'{script_path}/config.yml'

        with open(config_file, 'r') as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        print(f'ERROR: Config file {config_file} not found!')
        sys.exit()


def get_api_key(config):
    api_key = None

    if 'api_key' in config:
        api_key = config['api_key']
    else:
        raise Exception('No api_key configured in config.yml')

    return api_key


def fetch_data(config):
    api_key = get_api_key(config)

    r = httpx.post(
        f'https://api.runpod.io/graphql?api_key={api_key}',
        json={
            "query": """
                query myself {
                    myself {
                        id
                        authId
                        email
                        notifyPodsStale
                        notifyPodsGeneral
                        notifyLowBalance
                        creditAlertThreshold
                        notifyOther
                        currentSpendPerHr
                        machineQuota
                        referralEarned
                        signedTermsOfService
                        spendLimit
                        templateEarned
                        multiFactorEnabled
                        clientBalance
                        hostBalance
                        underBalance
                        minBalance
                        dailyCharges {
                            amount
                            updatedAt
                            diskCharges
                            podCharges
                            apiCharges
                            serverlessCharges
                            type
                        }
                        serverlessDiscount {
                            userId
                            type
                            discountFactor
                            expirationDate
                        }
                        spendDetails {
                            localStoragePerHour
                            networkStoragePerHour
                            gpuComputePerHour
                        }
                        creditCodes {
                            id
                            issuerId
                            createdAt
                            redeemedAt
                            amount
                        }
                        referral {
                            code
                            currentMonth {
                                totalReferrals
                                totalSpend
                            }
                        }
                        apiKeys {
                            id
                            permissions
                            createdAt
                        }
                        pubKey
                        containerRegistryCreds {
                            id
                            name
                            name
                            registryAuth
                        }
                        information {
                            firstName
                            lastName
                            addressLine1
                            addressLine2
                            countryCode
                            companyName
                            companyIdentification
                            taxIdentification
                        }
                        podTemplates {
                            id
                            name
                            imageName
                            isPublic
                            isRunpod
                            isServerless
                            ports
                            runtimeInMin
                            startJupyter
                            startScript
                            startSsh
                            volumeInGb
                            volumeMountPath
                            advancedStart
                            containerDiskInGb
                            containerRegistryAuthId
                            dockerArgs
                            earned
                            env {
                                key
                                value
                            }
                        }
                        pods {
                            name
                            id
                            desiredStatus
                            costPerHr
                            containerDiskInGb
                            volumeInGb
                            memoryInGb
                            vcpuCount
                            runtime {
                                uptimeInSeconds
                            }
                            machine {
                                podHostId
                            }
                        }
                        maxServerlessConcurrency
                        endpoints {
                            gpuIds
                            id
                            idleTimeout
                            name
                            networkVolumeId
                            locations
                            scalerType
                            scalerValue
                            template {
                                name
                                imageName
                            }
                            templateId
                            type
                            userId
                            version
                            workersMax
                            workersMin
                            workersStandby
                        }
                        networkVolumes {
                            id
                            name
                            size
                            dataCenterId
                        }
                        savingsPlans {
                            startTime
                            endTime
                            podId
                            gpuTypeId
                            pod {
                                name
                                id
                                desiredStatus
                                costPerHr
                                containerDiskInGb
                                volumeInGb
                                memoryInGb
                                vcpuCount
                            }
                            savingsPlanType
                            costPerHr
                            upfrontCost
                            planLength
                        }
                    }
                }
            """
        }
    )

    resp_json = r.json()

    if r.status_code == 200:
        if 'errors' in resp_json:
            raise Exception(f'ERROR: {str(resp_json)}')
        else:
            return resp_json['data']['myself']
    else:
        raise Exception(f'ERROR: HTTP status code: {r.status_code}, response: {str(resp_json)}')


def write_data(data):
    filename = 'runpod_endpoints.prom'
    output_file = os.path.join(config['textfile_path'], filename)
    tmp_output_file = f'{output_file}.$$'

    f = open(tmp_output_file, 'a')
    f.write('current_spend_per_hour{id="' + data['id'] + '"} ' + str(data['currentSpendPerHr']) + '\n')
    f.close()

    os.rename(tmp_output_file, output_file)


if __name__ == '__main__':
    script_path = os.path.dirname(__file__)
    config = load_config(script_path)
    data = fetch_data(config)
    print(json.dumps(data, indent=4, default=str))
    # write_data(data)
