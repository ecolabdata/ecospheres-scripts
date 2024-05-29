<?xml version="1.0" encoding="UTF-8"?>
<!--
Transforme une license libre en gmx:Anchor

https://ecospheres.gitbook.io/recommandations-iso-dcat/adaptation-des-metadonnees-iso-19139-pour-faciliter-la-transformation-en-dcat/faciliter-la-reconnaissance-des-licences

Le snippet:

    <gmd:resourceConstraints>
      <gmd:MD_LegalConstraints>
        <gmd:useConstraints>
          <gmd:MD_RestrictionCode codeList="http://standards.iso.org/iso/19139/resources/gmxCodelists.xml#MD_RestrictionCode"
                                  codeListValue="otherRestrictions"/>
        </gmd:useConstraints>
        <gmd:otherConstraints>
          <gco:CharacterString>Licence Ouverte version 2.0</gco:CharacterString>
        </gmd:otherConstraints>
      </gmd:MD_LegalConstraints>
    </gmd:resourceConstraints>
    
Devient:

    <gmd:resourceConstraint>
      <gmd:MD_LegalConstraints>
        <gmd:useConstraints>
          <gmd:MD_RestrictionCode codeList="http://standards.iso.org/iso/19139/resources/gmxCodelists.xml#MD_RestrictionCode"
                                  codeListValue="otherRestrictions"/>
        </gmd:useConstraints>
        <gmd:otherConstraints>
          <gmx:Anchor xlink:href="https://spdx.org/licenses/etalab-2.0">Licence Ouverte version 2.0</gmx:Anchor>
        </gmd:otherConstraints>
      </gmd:MD_LegalConstraints>
    <gmd:resourceConstraints>

NOTES:
- Seulement gmd:MD_LegalConstraints/gmd:useConstraints ou aussi gmd:MD_LegalConstraints/gmd:useLimitation ?
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"
                xmlns:gco="http://www.isotc211.org/2005/gco"
                xmlns:gmd="http://www.isotc211.org/2005/gmd"
                xmlns:gmx="http://www.isotc211.org/2005/gmx"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xmlns:geonet="http://www.fao.org/geonetwork"
                exclude-result-prefixes="#all">

  <xsl:variable name="licenses">
    <license code="AGPL-3.0-or-later" label="GNU Affero General Public License v3.0 or later"/>
    <license code="Apache-2.0"        label="Apache License 2.0"/>
    <license code="BSD-2-Clause"      label='BSD 2-Clause "Simplified" License'/>
    <license code="BSD-3-Clause"      label='BSD 3-Clause "New" or "Revised" License'/>
    <license code="CECILL-2.1"        label="CeCILL Free Software License Agreement v2.1"/>
    <license code="CECILL-B"          label="CeCILL-B Free Software License Agreement"/>
    <license code="CECILL-C"          label="CeCILL-C Free Software License Agreement"/>
    <license code="EPL-2.0"           label="Eclipse Public License 2.0"/>
    <license code="etalab-2.0"        label="Licence Ouverte version 2.0"/>
    <license code="EUPL-1.2"          label="European Union Public License 1.2"/>              
    <license code="GPL-3.0-or-later"  label="GNU General Public License v3.0 or later"/>
    <license code="LGPL-3.0-or-later" label="GNU Lesser General Public License v3.0 or later"/>
    <license code="MIT"               label="MIT License"/>
    <license code="MPL-2.0"           label="Mozilla Public License 2.0"/>
    <license code="ODbL-1.0"          label="ODC Open Database License (ODbL) version 1.0"/>
  </xsl:variable>

  <xsl:template match="/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/
                       gmd:resourceConstraints/gmd:MD_LegalConstraints[gmd:useConstraints]"
                priority="2">
    <gmd:MD_LegalConstraints>
      <xsl:copy-of select="gmd:accessConstraints"/>
      <xsl:copy-of select="gmd:useConstraints"/>
      <xsl:apply-templates select="gmd:otherConstraints"/>
    </gmd:MD_LegalConstraints>
  </xsl:template>

  <xsl:template match="gmd:otherConstraints">
    <xsl:variable name="label" select="gco:CharacterString"/>
    <xsl:variable name="code" select="$licenses/license[@label = $label]/@code"/>
    <xsl:choose>
      <xsl:when test="$code">
        <gmd:otherConstraints>
          <gmx:Anchor xlink:href="https://spdx.org/licenses/{$code}">
            <xsl:value-of select="$label"/>
          </gmx:Anchor>
        </gmd:otherConstraints>
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy-of select="."/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      GUI integration
  -->

  <xsl:template name="list-ecospheres-license-anchor">
    <suggestion process="ecospheres-license-anchor"/>
  </xsl:template>

  <xsl:template name="analyze-ecospheres-license-anchor">
    <xsl:param name="root"/>
    <!-- TODO: conditional trigger -->
    <suggestion process="ecospheres-license-anchor" id="{generate-id()}">
      <name xml:lang="en">
        Apply ecospheres-license-anchor
      </name>
      <operational>true</operational>
      <form/>
    </suggestion>
  </xsl:template>

  <!--
      Geonetwork internals
  -->
  
  <!-- Do a copy of every nodes and attributes -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Remove geonet:* elements. -->
  <xsl:template match="geonet:*" priority="2"/>
</xsl:stylesheet>
