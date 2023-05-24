from IPython.display import HTML, display
from jinja2 import Template
import math


# INPUTS
location = '8"-P-F1N-1323'  # Location of the inspection
material = "SA-516 Gr.72"  # Material of the component
P = 4.31   # MPA Design pressure
OD = 219  # mm outside diameter
tnom = 23.01  # mm nominal thickness
S = 172.37  # MPA allowable stress at maximum pressure
trd = 19.32  # Measured thickness awway from LTA in mm
tmm = 5.3  # minimum measured thickness in LTA
s = 100  # mm longitudnal length of LTA
c = 100  # mm circumferential length of LTA
FCA = 0  # Has been considerd 0 for this calculation only

E = 1  # Weld Joint Efficincy
MA = 0  # Mechanical ALlowance
Y = 0.4  # ASME B31 cofficient: 0.4 for CS & 0.7 for AS
RSFa = 0.9  # Allowable Remaining Strength Factor = 0.9
years = 12  # Operating Years
future_years = 0  # To calculate future corrosion allowance


# Helper function to calculate Mt value based on lemda
def calcMt(lemda):
    mt = 1.0010 - 0.014195 * lemda + 0.29090 * lemda**2 - 0.096420 * lemda**3 + 0.020890 * lemda**4 - 0.0030540 * lemda**5 + \
        2.9570e-4 * lemda**6 - 1.8462e-5 * lemda**7 + 7.1553e-7 * \
        lemda**8 - 1.5631e-8 * lemda**9 + 1.4656e-10 * lemda**10
    return round(mt, 3)


level1result = None
MAWPr = None
MAWPr_criteria = None
life = None


# Step 1: Determine the CTP
# find LTA and take readings in circumferencial and longitudnal direction

# step-2
# Determine the wall thickness to be used in the assessment using Equation (5.3) or Equation (5.4), as applicable.
tc = trd-FCA


# STEP-3
# Determine the minimum measured thickness in the LTA, tmm, and the dimensions, s and c (see paragraph 5.3.3.2.b) for the CTP.

# STEP-4: Determine the remaining thickness ratio using Equation (5.5) and the longitudinal flaw length parameter using Equation (5.6).
Rt = round((tmm-FCA)/tc, 3)
LOSS = tnom-trd
D = (OD-2*tnom) + 2*(FCA + LOSS)
λ = round((1.285*s) / math.sqrt((D*tc)), 3)

# STEP 5 – Check the limiting flaw size criteria; if the following requirements are satisfied, proceed to STEP 6; otherwise, the flaw is not acceptable per the Level 1 Assessment procedure.
limiting_flaw_size_criterion1 = Rt >= 0.2
limiting_flaw_size_criterion2 = tmm-FCA >= 1.3
limiting_flaw_size_criterion = limiting_flaw_size_criterion1 and limiting_flaw_size_criterion2

if not limiting_flaw_size_criterion:
    level1result = "The component is unacceptable to operate at the current design/maximum pressure"
else:
    #  f) STEP 6 – If the region of metal loss is categorized as an LTA
    #  (i.e. the LTA is not a groove), then proceed to STEP 7. If the region of metal loss is
    #  categorized as a groove and Equation (5.11) is satisfied, then proceed to STEP 7.
    #   Otherwise, the Level 1 assessment is not satisfied and proceed to paragraph 5.4.2.3.

    # g) STEP 7 – Determine the MAWP for the component (see Annex 2C, paragraph 2C.2) using the thickness from STEP 2.

    MAWP = round(((2*S*E)*(tmm-MA))/(OD-2*Y * (tmm-MA)), 3)

    # The parameter Mt in Equation (5.12) is determined from Table 5.2.
    Mt = calcMt(λ)  # by interpolation of values
    RSF = round(Rt/(1-(1/Mt) * (1-Rt)), 3)

    if RSF >= RSFa:
        MAWPr = MAWP
    else:
        MAWPr = round(MAWP * (RSF/RSFa), 3)

    if MAWPr >= P or MAWPr >= MAWP:
        MAWPr_criteria = "PASS"
        level1result = "The component is acceptable to operate at the current design/maximum pressure"
        # RLA
        tmin = round((P * OD)/(2*S * E + P * Y), 3)
        crate = round((tnom-tmm)/years, 7)
        life = round((tmm-tmin)/crate, 3)

    else:
        MAWPr_criteria = "FAIL"
        level1result = f"The component is unacceptable to operate at the current design/maximum pressure. It is recommended to limit the maximum pressure to {MAWPr} MPA for safe run."

    # #  Level-2 ssessment
    # Ao = s * tc
    # Ai = s * tmm
    # Art = Ai/Ao
    # RSFi = ((1-Art))/(1-(1-Mt)*Art)

    # if RSF >= RSFa :
    #   level2result = "PASS"
    # else:
    #   level2result = "FAIL"


# Generating Output Report
# Define your Jinja HTML template
template_string = """
<style>
    table {
        width: 100%;
        border-collapse: collapse;
    }



    p,
    td,
    div,
    li,
    span {
        font-family: 'Times New Roman', Times, serif;
        font-size: 12pt;
    }

    h1,
    h2,
    p,
    h4,
    h5,
    h6 {
        font-family: 'Times New Roman', Times, serif;
    }

    span.right {
        float: right;
    }

    span.ref {
        color: blue;
        font-size: 10pt;
        float: right;
    }

    p.heading {
        font-size: 14pt;
        font-weight: bold;
    }
</style>

<div>
    <p class='heading'>INPUTS:</p>
    <table>
        <tr>
            <td> Component Type </td>
            <td>: PIPE </td>
        </tr>
        <tr>
            <td>Location</td>
            <td>: {{location}} </td>
        </tr>
        <tr>
            <td>Material</td>
            <td>: {{material}} </td>
        </tr>
        <tr>
            <td> Design/Maximum Pressure (P) </td>
            <td>: {{P}} MPA </td>
        </tr>
        <tr>
            <td> Outer Diameter (OD) </td>
            <td>: {{OD}} mm </td>
        </tr>
        <tr>
            <td> Weld Joint Efficiency </td>
            <td>: {{E}} MPA </td>
        </tr>
        <tr>
            <td> Nominal Thickness (t<sub>nom</sub>) </td>
            <td>: {{tnom}} mm </td>
        </tr>
        <tr>
            <td> Minimum Measured Thickness (t <sub>mm</sub>) in LTA </td>
            <td>: {{tmm}} mm </td>
        </tr>
        <tr>
            <td> Minimum Measured Thickness (t <sub>rd</sub>) Away from LTA </td>
            <td>: {{trd}} mm </td>
        </tr>
        <tr>
            <td> Operating Years </td>
            <td>: {{years}} Years </td>
        </tr>
    </table>
    <p class='heading'>ASSESSMENT:</p>
    <ul>
        <li>
            ALLOWABLE STRESS(S) AT MAX TEMP : {{S}} MPA
        </li>
        <li>
            FUTURE CORROSION ALLOWANCE : {{FCA}} mm
        </li>
        <li>
            Wall thickness to be used in the assessment: <br />
            t<sub>c</sub> = t <sub>rd</sub> - FCA = {{tc}}
        </li>
        <li>
            Determination of the remaining thickness ratio (R<sub>t</sub>) and the longitudinal flaw length parameter
            (λ): <br />
            R<sub>t</sub> = (t <sub>mm</sub> - FCA ) / t<sub>c</sub> = {{Rt}} <br />
            λ = 1.285*s / √(D*t<sub>c</sub>) = {{ λ}}
        </li>
        <li>
            Checking the limiting flaw size criteria: <br />
            R<sub>t</sub> > 0.2 = {{ Rt > 0.2 }} <br />
            t<sub>mm</sub> - FCA > 1.3 = {{ tmm-FCA > 1.3 }} <br />
        </li>

        {# {% if eos_ver >= 4.22 -%}
        Detected EOS ver {{ eos_ver }}, using new command syntax.
        {% else -%}
        Detected EOS ver {{ eos_ver }}, using old command syntax.
        {% endif %} #}

        <li>
            Determination of the MAWP for the component: <br />
            MAWP = (2 * S * E * t<sub>mm</sub>) /(OD - 2 * Y * t<sub>mm</sub>) = {{ MAWP }} MPA <br />
        </li>
        <li>
            Determination of Folias Factor M<sub>t</sub>: <br />
            M<sub>t</sub> = {{Mt}} <span class="ref">Refer Table 5.2, API-579, 2016</span>
        </li>
        <li>
            Determination of remaining strength Factor RSF: <br />
            RSF = {{RSF}} <span class="ref">Refer para 5.12, API-579, 2016</span>
        </li>

        <li>
            Determination of reduced maximum allowable working pressure (MAWP<sub>r</sub>) for RSF: <br />
            MAWP<sub>r</sub> = {{MAWPr}} MPA <span class="ref">Refer Part 2, paragraph 2.4.2.2, API-579, 2016</span>
        </li>
        <li style="font-weight: bold;background-color:#e7e7e7">
           Level-1 Result:  {{level1result}}
        </li>
    </ul>   

    {% if life -%}

    <p class='heading'>REMAINNING LIFE ASSESSMENT:</p>
    <ul>
        <li>
            Minimum requred thickness (t<sub>min</sub>):
            t<sub>min</sub> = {{tmin}} mm <span class="ref">Refer paragraph 2C.3.3, API-579, 2016</span>
        </li>
        <li>
            Thinning Rate = {{crate}} mm/year
        </li>
        <li>
            Remainning Life: {{life}} Years
        </li>

    </ul>
    {% endif %}

</div>
"""
template = Template(template_string)
rendered_template = template.render({
    "location": location, "material": material,
    "P": P, "OD": OD, "S": S, "E": E, "tnom": tnom, "tmm": tmm, "years": years,
    "RSF": RSF, "RSFa": RSFa, "Mt": Mt, "trd": trd,
    "λ": λ, "Rt": Rt, "tc": tc, "FCA": FCA, "MAWP": MAWP, "MAWPr": MAWPr, "level1result": level1result,
    "limiting_flaw_size_criterion": limiting_flaw_size_criterion, "life": life, "crate": crate, "tmin": tmin,

})

display(HTML(rendered_template))
