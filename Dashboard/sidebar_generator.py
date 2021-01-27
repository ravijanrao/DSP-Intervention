import dash
import dash_core_components as dcc
import dash_html_components as html


LUT = {
    "STATUS": {
        0: "clearly not a humanitarian military intervention",
        1: "borderline case of humanitarian military intervention",
        2: "clear case of humanitarian military intervention",
    },
    "ENDTYPE": {
        0: "the intervention is ongoing at the time of coding",
        1: "end of violent emergency",
        2: "replacement by another humanitarian military intervention",
        3: "end of the humanitarian military intervention without a replacement by another while the emergency continued",
    },
    "ISSUE": {1: "terrritory", 2: "government", 3: "territory and government"},
    "NEWVIOL": {
        0: "the original emergency was ended and no new one occurred",
        1: "a new violent emergency occurred or the original emergency recurred",
        -88: "the item is not relevant, as the original emergency or the intervention was still ongoing or less than five years have passed after the intervention",
    },
    "UNSC": {0: "Not approved by UNSC", 2: "UNSC approved"},
    "REGIOORG": {
        0: "Not approved by regional organization.",
        1: "Partly approved by regional organization.",
        2: "Fully approved by regional organization.",
    },
    # Did the government in power of the target country permit the intervention?
    "GOVTPERM": {
        0: "Gov. in power did not permit the HMI.",
        1: "Gov. in power partly permitted the HMI.",
        2: "Gov. in power fully permitted the HMI.",
        -77: "Unclear",
        -99: "No data",
    },
    "CONTRA4": {0: "no", 1: "yes", -99: "unclear"},
    "CONTRA5": {
        0: "no, the intervener did not declare that intention",
        1: "yes, the intervener declared so",
        -99: "unclear",
    },
    "GROUNDFO": {0: "no", 1: "yes", -99: "no data"},
    "ACTIVE": {0: "Remained passive", 1: "Active"},
    "FORCE": {0: "no", 1: "yes", -77: "unclear", -99: "no data"},
}


# LUT2 = {'STATUS':
#                               {
#                                 0:'clearly not a humanitarian military intervention',
#                                 1:'borderline case of humanitarian military intervention',
#                                 2:'clear case of humanitarian military intervention'
#                               },
#                             'ENDTYPE':{
#                                 0:'the intervention is ongoing at the time of coding',
#                                 1:'end of violent emergency',
#                                 2:'replacement by another humanitarian military intervention',
#                                 3:'end of the humanitarian military intervention without a replacement by another while the emergency continued'
#                                  },
#                              'ISSUE': {
#                                   1:'terrritory',
#                                     2:'government',
#                                     3:'territory and government'
#                               },
#                               'NEWVIOL': {
#                                   0:'the original emergency was ended and no new one occurred',
#                                   1:'a new violent emergency occurred or the original emergency recurred',
#                                   -88:'the item is not relevant, as the original emergency or the intervention was still ongoing or less than five years have passed after the intervention'
#                               },
#                               'UNSC':{
#                                   0:'no',
#                                   2:'yes'
                                  
#                               },
#                               'REGIOORG':{
#                                   0:'no',
#                                   1: 'yes, but not all interveners or all activities',
#                                   2:'yes, all interveners and all their activities'                                
#                               },
#                               'GOVTPERM':{
#                                   0:'no',
#                                   1:'yes, but not all interveners or all activities',
#                                   2:'yes, all interveners and all their activities',
#                                   -77:'unclear',
#                                   -99: 'no data'
#                               },   
#                              'CONTRA4':{
#                                  0:'no',
#                                  1:'yes',
#                                  -99:'unclear'
                                 
#                              },
#                              'CONTRA5':{
#                                  0:'no, the intervener did not declare that intention',
#                                  1:'yes, the intervener declared so',
#                                  -99:'unclear'
                                 
#                              },
#                              'GROUNDFO':{
#                                  0:'no',
#                                  1:'yes',
#                                  -99: 'no data'
#                              },
#                              'ACTIVE':{
#                                  0: 'Remained passive',
#                                  1: 'Active'

#                              },
#                              'FORCE':{
#                                  0: 'no',
#                                  1: 'yes',
#                                  -77: 'unclear',
#                                  -99: 'no data'
#                              }
                             
#                              }

def sidebar_generator(hmi):
    #http://www.humanitarian-military-interventions.com/wp-content/uploads/2019/08/PRIF-data-set-HMI-codebook-v1-14.pdf
    c = []

    # c.append(html.H3("Main conflict characteristics"))
    
    c.append(html.Br())
    c.append(html.H5("Intervention timeline"))

    c.append(html.Div(className="tiny-timeline", children=
        [
            html.Div(className="timeline-left-txt bold", children=['START']),
            html.Div(className="timeline-fill"),
            html.Div(className="timeline-right-txt bold", children=['END'])
        ]
    ))

    c.append(html.Div(className="tiny-timeline", children=
        [
            html.Div(className="timeline-left-dot"),
            html.Div(className="timeline-line"),
            html.Div(className="timeline-right-dot")
        ]
    ))

    # HMI START/END DATES
    hmi_start = hmi.get('HMISTART').strftime("%m/%d-%Y").split('-')
    try:    
        hmi_end = hmi.get('HMIEND').strftime("%m/%d-%Y").split('-')
    except:
        hmi_end = ["ongoing", ""]

    
    c.append(html.Div(className="tiny-timeline", children=
        [
            html.Div(className="timeline-left-txt", children=[hmi_start[0],html.Br(), hmi_start[1]]),
            html.Div(className="timeline-fill"),
            html.Div(className="timeline-right-txt", children=[hmi_end[0], html.Br(), hmi_end[1]])
        ]
    ))
   
    c.append(html.H5("Intervening forces"))
    # INTERVENERS
    c.append(html.Span(className='intervener', children=hmi.get("INTERVEN1")))

    for intervener in [hmi.get("INTERVEN2"), hmi.get("INTERVEN3")]:
        if intervener != -88:
            c.append(html.Span(className='intervener', children=intervener))


    c.append(html.H5("Actors approval and motivations."))

    # c.append(html.H3("Description of approval/motivations:"))

    # Main conflict issue of the pre-existing violent emergency acording to UCDP
    # c.append(html.Div('Main conflict issue'))
    c.append(
        html.Ul(children = [
            # Main conflict issue of the pre-existing violent emergency acording to UCDP
            html.Li("Main issue over " + LUT['ISSUE'][hmi.get("ISSUE")]),

            # Did the United Nations Security Council mandate or approve the intervention?
            html.Li(LUT['UNSC'][hmi.get("UNSC")]),

            # Did a regional organization approve the military intervention?
            html.Li(LUT['REGIOORG'][hmi.get("REGIOORG")]),

            # Did the government in power of the target country permit the intervention?
            html.Li(LUT["GOVTPERM"][hmi.get("GOVTPERM")]),

            # Did the intervener stress that the people to be saved belong to their people or nation?
            html.Li("Intervener did not declare the intention to save it's 'own' people."),

            # Did the intervener stress that the people to be saved belong to their people or nation?
            html.Li("Intervener did not declare the intention to prevent a rival from assuming control."),
            ]   
        )
    )

    c.append(html.H5("Intervention characteristics"))

    max_deployed_forces = hmi.get("GROUNDNO")
    if max_deployed_forces == -88:
        max_deployed_forces = 0

    TATROOP = hmi.get("TATROOP")

    c.append(
        html.Ul(children = [

            #Best estimate of maximum number of combatants at the disposal of the primarily targeted side
            html.Li(f"Est. no. combatants at targeted side: {TATROOP:,}"),

            #In the case of deployed ground forces, what was their maximum size?
            html.Li(f"Max deployed forces: {max_deployed_forces:,}")
            ]   
        )
    )

    # Did the United Nations Security Council mandate or approve the intervention?
    # c.append(html.Div('UNSC mandate/approval?'))
    # c.append(html.Div(LUT['UNSC'][hmi.get("UNSC")]))

    # Did a regional organization approve the military intervention?
    # c.append(html.Div('Regionally approved?'))
    # c.append(html.Div(LUT['REGIOORG'][hmi.get("REGIOORG")]))

    # Did the government in power of the target country permit the intervention?
    # c.append(html.Div('Regional Gov permit?'))
    # c.append(html.Div(LUT["GOVTPERM"][hmi.get("GOVTPERM")]))

    # # Did the intervener stress that the people to be saved belong to their people or nation?
    # c.append(html.Div('Stress that people to be save belong to their people or nation?:'))
    # c.append(html.Div(LUT["CONTRA4"][hmi.get("CONTRA4")]))


    # Did the intervener declare the intention to prevent a rival from assuming control over the target country?
    # c.append(html.Div('Declare intention to prevent a rival from assuming control?:',
    # **{'data-tooltip':'Did the intervener declare the intention to prevent a rival from assuming control over the target country?'}))
    # c.append(html.Div(LUT["CONTRA5"][hmi.get("CONTRA5")]))
    

    # c.append(html.H3("Basic Intervention Characteristics:"))

    #Best estimate of maximum number of combatants at the disposal of the primarily targeted side
    # c.append(html.Div('Best est. combatants targeted side.'))
    # c.append(html.Div(hmi.get("TATROOP")))

    #Were ground forces deployed in the target country?
    # c.append(html.Div('Were ground forces deployed in the target country?'))
    # c.append(html.Div(LUT["GROUNDFO"][hmi.get("GROUNDFO")]))

    #In the case of deployed ground forces, what was their maximum size?
    # if hmi.get("GROUNDNO") != -88:
    #     c.append(html.Div('Max deployed forces'))
    #     c.append(html.Div(hmi.get("GROUNDNO")))

    # #Did the intervening forces actively fulfil their mandate or did they remain passive?
    # c.append(html.Div('Interveners actively?'))
    # c.append(html.Div(LUT["ACTIVE"][hmi.get("ACTIVE")]))
        
    #Did the state or organization that deployed the intervention troops authorize the use of force for any activity?
    # c.append(html.Div('Was force authorized?'))
    # c.append(html.Div(LUT["FORCE"][hmi.get("FORCE")]))


    return html.Div(c)
