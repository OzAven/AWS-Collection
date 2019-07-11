import boto3
from termcolor import colored

def print_ids_and_tags(instance, file):
    count = 1
    text_file = file
    if instance.tags is None:
        print instance.id + " " + " - Has no tag"
        text_file.write('\n')
        text_file.write('No tags')

    else:
        for tag in instance.tags:
            text_file.write('\n')
            text_file.write('%s. %s' % (str(count), tag[u'Value']))
            count += 1

def elb_tags_per_region(region_name, file):
    conn = boto3.Session(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    res = conn.client('elb', region_name=region_name)
    all_elbs_in_region = res.describe_load_balancers()['LoadBalancerDescriptions']

    elbs = []
    for elb in all_elbs_in_region:
        elbs.append(elb[u'LoadBalancerName'])

    if not elbs:
        print colored("[+] No load balancers in ", 'yellow', attrs=['bold']) + colored(str(region_name), 'yellow', attrs=['bold'])
        return
    else:
        text_file = file
        text_file.write("ELB\n\n")

        for elb in all_elbs_in_region:
            print colored("[+] Collecting information for - ", 'blue') + colored(elb[u'LoadBalancerName'], 'blue')
            text_file.write(
                '\n\nAWS Name - %s | DNS Name - %s | VPC ID - %s | Availability Zones - %s' % (
                elb[u'LoadBalancerName'], elb[u'DNSName'], elb[u'VPCId'], elb[u'AvailabilityZones']))

            res_elb_tags = res.describe_tags(LoadBalancerNames=[elb[u'LoadBalancerName']])['TagDescriptions'][0]['Tags']
            count = 1

            if not res_elb_tags:
                continue
            else:
                text_file.write('\nTags:')
                for tag in res_elb_tags:
                    text_file.write('\n%s. Key: %s | Value: %s' % (str(count), tag[u'Key'], tag[u'Value']))
                    count += 1
            print colored("[+] Done collecting information for - ", 'blue') + colored(elb[u'LoadBalancerName'], 'blue')

    print colored("[+] Done with EC2 on region", 'yellow', attrs=['bold']) + colored(region_name, 'yellow', attrs=['bold'])

def ec2_tags_per_region(region_name, file):
    conn = boto3.Session(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    res = conn.resource('ec2', region_name=region_name)

    text_file = file
    text_file.write("EC2\n\n")

    for instance in res.instances.all():
        print colored("[+] Collecting information for - ", 'blue') + colored(instance.id, 'blue')
        text_file.write('\n\nID - %s | DNSname - %s | Private_IP - %s | Public_IP - %s' % (instance.id, instance.public_dns_name, instance.private_ip_address, instance.public_ip_address))
        print_ids_and_tags(instance, text_file)
        print colored("[+] Done collecting information for - ", 'blue') + colored(instance.id, 'blue')

    print colored("[+] Done with EC2 on region", 'yellow', attrs=['bold']) + colored(region_name, 'yellow', attrs=['bold'])

def get_regions():
    conn = boto3.Session(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    res = conn.client('ec2', region_name='us-east-1')
    all_regions = res.describe_regions()['Regions']
    regions = []
    for region in all_regions:
        regions.append(region[u'RegionName'])
    return regions


def main():
    global AWS_ACCESS_KEY_ID
    global AWS_SECRET_ACCESS_KEY
    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''

    print colored("[+] Generating list of available regions..", 'yellow', attrs=['bold'])
    total_regions = get_regions()

    for region in total_regions:
        print colored("[+] Available region: ", 'green') + colored(region, 'green')

    for region in total_regions:
        print colored("[+] Now running EC2 tags collection for ", 'yellow', attrs=['bold']) + colored(region, 'yellow', attrs=['bold'])
        with open('ec2/%s-ec2.txt' % region, 'w') as text_file:
            ec2_tags_per_region(region, text_file)

    print colored("[+] Done running for EC2 instances", 'yellow', attrs=['bold'])

    for region in total_regions:
        print colored("[+] Now running ELB tags collection for ", 'yellow', attrs=['bold']) + colored(region, 'yellow', attrs=['bold'])
        with open('elb/%s-elb.txt' % region, 'w') as text_file:
            elb_tags_per_region(region, text_file)

    print colored("[+] Done running for ELB instances", 'yellow', attrs=['bold'])

    print colored("[+] Collection script finished successfully..!", 'yellow', attrs=['bold'])

if __name__ == "__main__":
    main()


